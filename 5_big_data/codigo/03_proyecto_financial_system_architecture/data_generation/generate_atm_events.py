"""
generate_atm_events.py
----------------------
Genera eventos de cajeros automáticos (ATM) sintéticos para Lumina Bank.
Los ATMs representan la infraestructura física subutilizada (pain point del caso).

Uso:
    python generate_atm_events.py --output data/atm_events.csv --atms 500 --events 200000
"""

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta

# Distribución de ATMs por distrito (proporcional a población)
ATM_DISTRICT_WEIGHTS = {
    "Distrito Norte":       12,
    "Distrito Sur":         10,
    "Distrito Este":        8,
    "Distrito Oeste":       8,
    "Distrito Central":     25,
    "Distrito Financiero":  20,
    "Distrito Residencial": 10,
    "Distrito Industrial":  7,
}

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

LEGACY_BANKS = [
    "BancoAlpha", "BancoBeta", "BancoGamma", "BancoDelta",
    "BancoEpsilon", "BancoZeta", "BancoEta", "BancoTheta",
    "BancoIota", "BancoKappa", "BancoLambda", "BancoMu"
]

EVENT_TYPES = [
    "RETIRO_EFECTIVO",
    "CONSULTA_SALDO",
    "DEPOSITO",
    "TRANSFERENCIA",
    "PAGO_SERVICIO",
    "ERROR_TARJETA",
    "TARJETA_BLOQUEADA",
    "SIN_EFECTIVO",          # ATM sin fondos - infraestructura subutilizada
    "MANTENIMIENTO",
    "REINICIO_SISTEMA",
]

EVENT_WEIGHTS = [40, 20, 10, 10, 8, 4, 3, 2, 2, 1]

ATM_STATUSES = ["OPERATIVO", "MANTENIMIENTO", "SIN_EFECTIVO", "FUERA_SERVICIO"]


def generate_atm_fleet(num_atms: int) -> list[dict]:
    """Genera una flota de ATMs distribuidos por distrito."""
    districts = list(ATM_DISTRICT_WEIGHTS.keys())
    weights = list(ATM_DISTRICT_WEIGHTS.values())

    atms = []
    for _ in range(num_atms):
        district = random.choices(districts, weights=weights)[0]
        base_lat, base_lon = DISTRICT_COORDS[district]
        atms.append({
            "atm_id": f"ATM-{uuid.uuid4().hex[:8].upper()}",
            "district": district,
            "lat": round(base_lat + random.uniform(-0.08, 0.08), 6),
            "lon": round(base_lon + random.uniform(-0.08, 0.08), 6),
            "bank_owner": random.choice(LEGACY_BANKS),
            "capacity_daily_usd": random.choice([5000, 10000, 20000, 50000]),
            "status": random.choices(
                ATM_STATUSES,
                weights=[80, 8, 7, 5]  # 80% operativo, reflejando pain point de subutilización
            )[0],
        })
    return atms


def generate_atm_event(atm: dict, client_ids: list[str], base_time: datetime) -> dict:
    event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)[0]

    # Eventos de sistema no necesitan client_id
    if event_type in ("SIN_EFECTIVO", "MANTENIMIENTO", "REINICIO_SISTEMA"):
        client_id = None
        amount = 0.0
    else:
        client_id = random.choice(client_ids) if client_ids else None
        amount = round(random.uniform(20, 1000), 2) if event_type in (
            "RETIRO_EFECTIVO", "DEPOSITO", "TRANSFERENCIA", "PAGO_SERVICIO"
        ) else 0.0

    # Timestamp: picos antes y después del horario laboral
    hour_weights = [1,1,1,1,1,2, 4,8,7,6,5,6, 7,7,6,5,5,7, 7,5,4,3,2,1]
    hour = random.choices(range(24), weights=hour_weights)[0]
    event_time = base_time.replace(
        hour=hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )

    return {
        "event_id": f"EVT-{uuid.uuid4().hex[:16].upper()}",
        "atm_id": atm["atm_id"],
        "client_id": client_id or "",
        "district": atm["district"],
        "bank_owner": atm["bank_owner"],
        "lat": atm["lat"],
        "lon": atm["lon"],
        "event_timestamp": event_time.isoformat(),
        "event_type": event_type,
        "amount": amount,
        "currency": "USD",
        "atm_status": atm["status"],
        "success": event_type not in ("ERROR_TARJETA", "TARJETA_BLOQUEADA", "SIN_EFECTIVO"),
        "response_time_ms": random.randint(200, 8000),
    }


def generate_atm_events(num_atms: int, num_events: int, output_path: str, client_ids: list[str]):
    print(f"[INFO] Generando flota de {num_atms} ATMs y {num_events:,} eventos...")
    atm_fleet = generate_atm_fleet(num_atms)

    # Guardar también el catálogo de ATMs
    atm_catalog_path = output_path.replace("atm_events", "atm_catalog")
    with open(atm_catalog_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(atm_fleet[0].keys()))
        writer.writeheader()
        writer.writerows(atm_fleet)
    print(f"[OK] Catálogo de ATMs guardado: {atm_catalog_path}")

    # Generar eventos
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    fieldnames = [
        "event_id", "atm_id", "client_id", "district", "bank_owner",
        "lat", "lon", "event_timestamp", "event_type", "amount", "currency",
        "atm_status", "success", "response_time_ms"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(num_events):
            atm = random.choice(atm_fleet)
            days_offset = random.randint(0, 89)
            base_time = start_date + timedelta(days=days_offset)
            event = generate_atm_event(atm, client_ids, base_time)
            writer.writerow(event)
            if (i + 1) % 50000 == 0:
                print(f"  → {i + 1:,} eventos generados...")

    print(f"[OK] Archivo de eventos ATM: {output_path}")


def load_client_ids_simple(clients_file: str, max_n: int = 5000) -> list[str]:
    ids = []
    try:
        with open(clients_file, "r") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= max_n:
                    break
                ids.append(row["client_id"])
    except FileNotFoundError:
        print(f"[WARN] {clients_file} no encontrado. Generando IDs de cliente genéricos.")
        ids = [f"C-{uuid.uuid4().hex[:12].upper()}" for _ in range(1000)]
    return ids


def main():
    parser = argparse.ArgumentParser(description="Generador de eventos ATM – Lumina Bank")
    parser.add_argument("--output", default="data/atm_events.csv")
    parser.add_argument("--atms", type=int, default=500, help="Número de ATMs en la flota")
    parser.add_argument("--events", type=int, default=200000, help="Número de eventos a generar")
    parser.add_argument("--clients-file", default="data/clients.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)

    client_ids = load_client_ids_simple(args.clients_file)
    print(f"[INFO] {len(client_ids)} client IDs cargados para eventos ATM.")
    generate_atm_events(args.atms, args.events, args.output, client_ids)


if __name__ == "__main__":
    main()
