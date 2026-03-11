"""
generate_transactions.py
------------------------
Genera transacciones financieras sintéticas para Lumina Bank.
Incluye patrones de fraude realistas para el pipeline de detección.

Uso:
    python generate_transactions.py \
        --clients-file data/clients.csv \
        --output data/transactions.csv \
        --count 500000
"""

import argparse
import csv
import json
import random
import uuid
from datetime import datetime, timedelta

# Configuración
CHANNELS = ["MOBILE", "ATM", "WEB", "BRANCH", "POS", "API_TRANSFER"]
TRANSACTION_TYPES = ["COMPRA", "TRANSFERENCIA", "RETIRO", "DEPOSITO", "PAGO_SERVICIO", "INVERSION"]
MERCHANT_CATEGORIES = [
    "SUPERMERCADO", "RESTAURANTE", "GASOLINERA", "FARMACIA", "ROPA_CALZADO",
    "TRANSPORTE", "EDUCACION", "SALUD", "ENTRETENIMIENTO", "TECNOLOGIA",
    "HOGAR", "VIAJES", "SERVICIOS_FINANCIEROS", "TELECOMUNICACIONES", "OTROS"
]

# Coordenadas base por distrito de DataLandia
DISTRICT_COORDS = {
    "Distrito Norte":       (-12.04, -77.05),
    "Distrito Sur":         (-12.18, -77.01),
    "Distrito Este":        (-12.06, -76.90),
    "Distrito Oeste":       (-12.10, -77.15),
    "Distrito Central":     (-12.07, -77.03),
    "Distrito Financiero":  (-12.05, -77.04),
    "Distrito Residencial": (-12.09, -77.08),
    "Distrito Industrial":  (-12.14, -76.95),
}


def load_client_ids(clients_file: str, max_clients: int = 10000) -> list[dict]:
    """Carga una muestra de clientes desde el CSV generado."""
    clients = []
    with open(clients_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_clients:
                break
            clients.append(row)
    return clients


def simulate_fraud(client: dict, amount: float, timestamp: datetime) -> tuple[bool, float, str]:
    """
    Simula detección de fraude con reglas simples.
    Retorna: (is_fraud, fraud_score, rule_triggered)
    """
    fraud_score = 0.0
    rules = []

    # Regla 1: Monto alto inusual para cliente de bajo saldo
    avg_balance = float(client.get("balance", 1000))
    if amount > avg_balance * 2:
        fraud_score += 0.4
        rules.append("MONTO_EXCEDE_SALDO_2X")

    # Regla 2: Hora inusual (2am - 5am)
    if 2 <= timestamp.hour <= 5:
        fraud_score += 0.2
        rules.append("HORA_INUSUAL")

    # Regla 3: Cliente de alto riesgo
    if client.get("risk_tier") in ("ALTO", "MUY_ALTO"):
        fraud_score += 0.2
        rules.append("CLIENTE_ALTO_RIESGO")

    # Riesgo adicional aleatorio (fraude no detectado por reglas simples)
    noise = random.uniform(0, 0.15)
    fraud_score = min(1.0, fraud_score + noise)

    is_fraud = fraud_score >= 0.6
    rule_str = "|".join(rules) if rules else "NINGUNA"

    return is_fraud, round(fraud_score, 3), rule_str


def generate_transaction(client: dict, base_time: datetime) -> dict:
    # Timestamp con distribución realista: picos en mañana (8-10) y mediodía (12-14)
    hour_weights = [1,1,1,1,1,1,1,3, 8,8,6,6, 8,8,6,5, 4,4,3,3, 3,2,2,1]
    hour = random.choices(range(24), weights=hour_weights)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    tx_time = base_time.replace(hour=hour, minute=minute, second=second)

    channel = random.choices(
        CHANNELS,
        weights=[35, 20, 25, 5, 10, 5]  # Mobile dominante
    )[0]
    tx_type = random.choices(
        TRANSACTION_TYPES,
        weights=[40, 25, 15, 5, 12, 3]
    )[0]

    district = client.get("district", "Distrito Central")
    base_lat, base_lon = DISTRICT_COORDS.get(district, (-12.07, -77.03))

    # Pequeña variación en coordenadas
    lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
    lon = round(base_lon + random.uniform(-0.05, 0.05), 6)

    balance = float(client.get("balance", 500))
    amount = round(random.lognormal(mean=4.5, sigma=1.2), 2)  # Distribución log-normal realista
    amount = min(amount, balance * 1.05)  # No puede exceder mucho el saldo
    amount = max(0.1, amount)

    is_fraud, fraud_score, rule_triggered = simulate_fraud(client, amount, tx_time)

    return {
        "transaction_id": f"TX-{uuid.uuid4().hex[:16].upper()}",
        "client_id": client["client_id"],
        "account_type": client.get("account_type", "CORRIENTE"),
        "district": district,
        "event_timestamp": tx_time.isoformat(),
        "amount": amount,
        "currency": "USD",
        "channel": channel,
        "transaction_type": tx_type,
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "merchant_id": f"MRC-{random.randint(1000, 9999)}",
        "lat": lat,
        "lon": lon,
        "is_fraud": is_fraud,
        "fraud_score": fraud_score,
        "fraud_rule_triggered": rule_triggered,
        "status": "DECLINED" if is_fraud and fraud_score > 0.8 else "APPROVED",
        "processing_time_ms": random.randint(50, 2500),
    }


def generate_transactions(clients: list[dict], count: int, output_path: str, output_format: str = "csv"):
    """Genera N transacciones distribuidas entre los clientes dados."""
    print(f"[INFO] Generando {count:,} transacciones → {output_path}")

    # Fecha base: últimos 90 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    fieldnames = [
        "transaction_id", "client_id", "account_type", "district",
        "event_timestamp", "amount", "currency", "channel", "transaction_type",
        "merchant_category", "merchant_id", "lat", "lon",
        "is_fraud", "fraud_score", "fraud_rule_triggered", "status", "processing_time_ms"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        if output_format == "csv":
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(count):
                client = random.choice(clients)
                days_offset = random.randint(0, 89)
                base_time = start_date + timedelta(days=days_offset)
                tx = generate_transaction(client, base_time)
                writer.writerow(tx)
                if (i + 1) % 100000 == 0:
                    print(f"  → {i + 1:,} transacciones generadas...")
        else:  # JSON Lines (para Pub/Sub simulation)
            for i in range(count):
                client = random.choice(clients)
                days_offset = random.randint(0, 89)
                base_time = start_date + timedelta(days=days_offset)
                tx = generate_transaction(client, base_time)
                f.write(json.dumps(tx) + "\n")
                if (i + 1) % 100000 == 0:
                    print(f"  → {i + 1:,} transacciones generadas...")

    print(f"[OK] Archivo generado: {output_path}")

    # Resumen estadístico
    print(f"\n[STATS] Resumen de generación:")
    print(f"  - Clientes distintos aproximados: {min(len(clients), count)}")
    print(f"  - Fraudes estimados (~5%): {int(count * 0.05):,}")


def main():
    parser = argparse.ArgumentParser(description="Generador de transacciones sintéticas – Lumina Bank")
    parser.add_argument("--clients-file", default="data/clients.csv")
    parser.add_argument("--output", default="data/transactions.csv")
    parser.add_argument("--count", type=int, default=500000)
    parser.add_argument("--format", choices=["csv", "jsonl"], default="csv")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-clients", type=int, default=10000,
                        help="Máximo de clientes a cargar en memoria desde el CSV")
    args = parser.parse_args()

    random.seed(args.seed)

    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)

    print(f"[INFO] Cargando clientes desde {args.clients_file}...")
    clients = load_client_ids(args.clients_file, args.max_clients)
    print(f"[INFO] {len(clients):,} clientes cargados.")

    generate_transactions(clients, args.count, args.output, args.format)


if __name__ == "__main__":
    main()
