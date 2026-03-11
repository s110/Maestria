"""
pubsub_producer.py
------------------
Simula el flujo de transacciones en tiempo real publicando mensajes JSON
al topic de Cloud Pub/Sub de Lumina Bank.

Modela los picos de carga en horarios de pago (pain point de congestión).

Uso:
    # Modo producción continua
    python pubsub_producer.py --project project-b028d063-61aa-48a0-ad5

    # Modo simulación rápida (N mensajes y termina)
    python pubsub_producer.py --count 1000 --rate 50

    # Modo dry-run (sin Pub/Sub, solo imprime los mensajes)
    python pubsub_producer.py --dry-run --count 20
"""

import argparse
import csv
import json
import random
import time
import uuid
from concurrent.futures import TimeoutError
from datetime import datetime

# ── Intentar importar el cliente Pub/Sub ──────────────────────────────────────
try:
    from google.cloud import pubsub_v1
    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False
    print("[WARN] google-cloud-pubsub no instalado. Solo disponible en modo --dry-run.")

# ── Configuración ─────────────────────────────────────────────────────────────
PROJECT_ID = "project-b028d063-61aa-48a0-ad5"
TOPIC_ID   = "lumina-transactions-stream"

CHANNELS = ["MOBILE", "ATM", "WEB", "BRANCH", "POS", "API_TRANSFER"]
CHANNEL_WEIGHTS = [35, 20, 25, 5, 10, 5]
TX_TYPES = ["COMPRA", "TRANSFERENCIA", "RETIRO", "DEPOSITO", "PAGO_SERVICIO"]
TX_WEIGHTS = [40, 25, 15, 5, 15]
MERCHANT_CATEGORIES = [
    "SUPERMERCADO", "RESTAURANTE", "GASOLINERA", "FARMACIA", "TRANSPORTE",
    "EDUCACION", "SALUD", "ENTRETENIMIENTO", "TECNOLOGIA", "TELECOMUNICACIONES",
]
DISTRICTS = [
    "Distrito Norte", "Distrito Sur", "Distrito Este", "Distrito Oeste",
    "Distrito Central", "Distrito Financiero", "Distrito Residencial", "Distrito Industrial"
]
DISTRICT_COORDS = {
    "Distrito Norte": (-12.04, -77.05), "Distrito Sur": (-12.18, -77.01),
    "Distrito Este": (-12.06, -76.90), "Distrito Oeste": (-12.10, -77.15),
    "Distrito Central": (-12.07, -77.03), "Distrito Financiero": (-12.05, -77.04),
    "Distrito Residencial": (-12.09, -77.08), "Distrito Industrial": (-12.14, -76.95),
}


def get_current_tps(hour: int) -> float:
    """
    Devuelve transacciones por segundo estimadas según la hora.
    Modela los picos de pago (pain point de latencia de DataBank).
    """
    tps_by_hour = {
        0: 5,  1: 3,  2: 2,  3: 2,  4: 2,  5: 5,
        6: 15, 7: 30, 8: 80, 9: 120, 10: 100, 11: 90,
        12: 130, 13: 140, 14: 110, 15: 100, 16: 90, 17: 95,
        18: 80, 19: 70, 20: 60, 21: 50, 22: 35, 23: 20,
    }
    return tps_by_hour.get(hour, 50)


def load_client_sample(clients_file: str, n: int = 2000) -> list[dict]:
    clients = []
    try:
        with open(clients_file, "r") as f:
            for i, row in enumerate(csv.DictReader(f)):
                if i >= n:
                    break
                clients.append(row)
        print(f"[INFO] {len(clients)} clientes cargados desde {clients_file}")
    except FileNotFoundError:
        print(f"[WARN] {clients_file} no encontrado. Usando clientes genéricos.")
        for _ in range(500):
            clients.append({
                "client_id": f"C-{uuid.uuid4().hex[:12].upper()}",
                "district": random.choice(DISTRICTS),
                "balance": random.uniform(100, 10000),
                "risk_tier": random.choice(["BAJO", "MEDIO", "ALTO"]),
            })
    return clients


def build_transaction_message(client: dict) -> dict:
    """Construye el payload JSON de una transacción en tiempo real."""
    district = client.get("district", random.choice(DISTRICTS))
    base_lat, base_lon = DISTRICT_COORDS.get(district, (-12.07, -77.03))
    balance = float(client.get("balance", 1000))
    amount = round(min(random.lognormal(4.5, 1.2), balance * 1.05), 2)
    amount = max(0.1, amount)

    return {
        "transaction_id": f"TX-{uuid.uuid4().hex[:16].upper()}",
        "client_id": client.get("client_id", f"C-{uuid.uuid4().hex[:12].upper()}"),
        "account_type": client.get("account_type", "CORRIENTE"),
        "district": district,
        "event_timestamp": datetime.utcnow().isoformat() + "Z",
        "amount": amount,
        "currency": "USD",
        "channel": random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
        "transaction_type": random.choices(TX_TYPES, weights=TX_WEIGHTS)[0],
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "merchant_id": f"MRC-{random.randint(1000, 9999)}",
        "lat": round(base_lat + random.uniform(-0.05, 0.05), 6),
        "lon": round(base_lon + random.uniform(-0.05, 0.05), 6),
        "status": "PENDING",
        "source": "lumina-producer-v1",
    }


def publish_message(publisher, topic_path: str, message: dict) -> None:
    """Publica un mensaje JSON en el topic Pub/Sub."""
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(
        topic_path,
        data=data,
        district=message.get("district", ""),
        channel=message.get("channel", ""),
    )
    return future


def run_producer(
    project_id: str,
    topic_id: str,
    clients: list[dict],
    count: int | None = None,
    rate_override: float | None = None,
    dry_run: bool = False,
    simulate_peaks: bool = True,
):
    """
    Bucle principal del productor.
    Si count es None, corre indefinidamente (modo daemon).
    """
    if not dry_run:
        if not PUBSUB_AVAILABLE:
            raise RuntimeError("google-cloud-pubsub no está instalado. Instala con: pip install google-cloud-pubsub")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        print(f"[INFO] Publicando en: {topic_path}")
    else:
        publisher = None
        topic_path = f"projects/{project_id}/topics/{topic_id}"
        print(f"[DRY-RUN] no se publicará en Pub/Sub. Topic destino: {topic_path}")

    print(f"[INFO] Iniciando productor de transacciones...")
    print(f"[INFO] Clientes disponibles: {len(clients)}")
    print(f"[INFO] Mensajes a enviar: {count if count else 'ilimitado (Ctrl+C para detener)'}")
    print(f"[INFO] Picos horarios simulados: {simulate_peaks}")
    print("")

    sent = 0
    errors = 0
    start_time = time.time()
    futures = []

    try:
        while count is None or sent < count:
            hour = datetime.now().hour
            tps = rate_override if rate_override else (get_current_tps(hour) if simulate_peaks else 10)
            sleep_interval = 1.0 / tps if tps > 0 else 1.0

            client = random.choice(clients)
            message = build_transaction_message(client)

            if dry_run:
                print(f"[MSG {sent+1}] {json.dumps(message, indent=2)}")
                time.sleep(min(sleep_interval, 0.1))  # No ralentizar demasiado en dry-run
            else:
                try:
                    future = publish_message(publisher, topic_path, message)
                    futures.append(future)
                    # Resoluciones en batch cada 100 mensajes para no bloquear
                    if len(futures) >= 100:
                        for f in futures:
                            try:
                                f.result(timeout=5)
                            except Exception as e:
                                errors += 1
                        futures = []
                    time.sleep(sleep_interval)
                except Exception as e:
                    print(f"[ERROR] Al publicar mensaje: {e}")
                    errors += 1

            sent += 1

            # Log de progreso
            if sent % 1000 == 0:
                elapsed = time.time() - start_time
                actual_tps = sent / elapsed if elapsed > 0 else 0
                print(f"[PROGRESS] {sent:,} mensajes enviados | TPS real: {actual_tps:.1f} | Errores: {errors}")

    except KeyboardInterrupt:
        print("\n[INFO] Productor detenido por el usuario.")

    # Resolver futuros pendientes
    if not dry_run and futures:
        for f in futures:
            try:
                f.result(timeout=10)
            except Exception:
                errors += 1

    elapsed = time.time() - start_time
    print(f"\n[RESUMEN]")
    print(f"  Total enviados : {sent:,}")
    print(f"  Errores        : {errors}")
    print(f"  Tiempo total   : {elapsed:.1f}s")
    print(f"  TPS promedio   : {sent/elapsed:.1f}" if elapsed > 0 else "")


def main():
    parser = argparse.ArgumentParser(description="Pub/Sub Transaction Producer – Lumina Bank")
    parser.add_argument("--project", default=PROJECT_ID)
    parser.add_argument("--topic", default=TOPIC_ID)
    parser.add_argument("--clients-file", default="data/clients.csv")
    parser.add_argument("--count", type=int, default=None,
                        help="Número de mensajes. Sin este argumento: modo continuo.")
    parser.add_argument("--rate", type=float, default=None,
                        help="TPS fijo. Si no se especifica, simula picos horarios reales.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Imprime los mensajes sin publicar en Pub/Sub")
    parser.add_argument("--no-peaks", action="store_true",
                        help="Desactiva la simulación de picos horarios")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)

    clients = load_client_sample(args.clients_file)
    run_producer(
        project_id=args.project,
        topic_id=args.topic,
        clients=clients,
        count=args.count,
        rate_override=args.rate,
        dry_run=args.dry_run,
        simulate_peaks=not args.no_peaks,
    )


if __name__ == "__main__":
    main()
