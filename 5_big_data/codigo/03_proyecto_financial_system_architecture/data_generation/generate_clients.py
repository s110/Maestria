"""
generate_clients.py
-------------------
Genera perfiles de clientes sintéticos para Lumina Bank.

Uso:
    python generate_clients.py --output data/clients.csv --count 50000
"""

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta

# Configuración
DISTRICTS = [
    "Distrito Norte", "Distrito Sur", "Distrito Este", "Distrito Oeste",
    "Distrito Central", "Distrito Financiero", "Distrito Residencial", "Distrito Industrial"
]
LEGACY_BANKS = [
    "BancoAlpha", "BancoBeta", "BancoGamma", "BancoDelta",
    "BancoEpsilon", "BancoZeta", "BancoEta", "BancoTheta",
    "BancoIota", "BancoKappa", "BancoLambda", "BancoMu"
]
ACCOUNT_TYPES = ["CORRIENTE", "AHORROS", "NOMINA", "INVERSION", "EMPRESARIAL"]
DIGITAL_PREFS = ["ALTA", "MEDIA", "BAJA"]  # Preferencia digital (nativa vs. legacy)
RISK_TIERS = ["BAJO", "MEDIO", "ALTO", "MUY_ALTO"]
FIRST_NAMES = [
    "Ana", "Luis", "María", "Carlos", "Sofia", "Jorge", "Elena", "Pedro",
    "Laura", "Miguel", "Carmen", "José", "Isabel", "Diego", "Rosa", "Andrés",
    "Patricia", "Ricardo", "Valeria", "Sergio", "Natalia", "Pablo", "Daniela",
    "Alejandro", "Fernanda", "Gabriel", "Monica", "Roberto", "Claudia", "Hector"
]
LAST_NAMES = [
    "García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Flores", "Rivera", "Morales", "Jiménez", "Cruz", "Reyes",
    "Ramos", "Vargas", "Herrera", "Medina", "Castro", "Guerrero", "Ortiz", "Silva",
    "Mendoza", "Rojas", "Delgado", "Ríos", "Aguilar", "Vega", "Núñez"
]


def random_date(start_year=2015, end_year=2024) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")


def assign_digital_preference(age: int) -> str:
    """Adultos mayores → BAJA; jóvenes → ALTA. Refleja el pain point demográfico."""
    if age >= 60:
        return random.choices(["BAJA", "MEDIA"], weights=[0.75, 0.25])[0]
    elif age >= 40:
        return random.choices(["MEDIA", "ALTA", "BAJA"], weights=[0.5, 0.35, 0.15])[0]
    else:
        return random.choices(["ALTA", "MEDIA"], weights=[0.8, 0.2])[0]


def generate_client(client_id: str) -> dict:
    age = random.randint(18, 80)
    district = random.choice(DISTRICTS)
    digital_pref = assign_digital_preference(age)
    account_type = random.choice(ACCOUNT_TYPES)
    legacy_bank = random.choice(LEGACY_BANKS)

    # Saldo basado en tipo de cuenta
    if account_type == "EMPRESARIAL":
        balance = round(random.uniform(5000, 500000), 2)
    elif account_type == "INVERSION":
        balance = round(random.uniform(1000, 100000), 2)
    else:
        balance = round(random.uniform(10, 20000), 2)

    credit_score = round(random.gauss(600, 100), 1)
    credit_score = max(300, min(850, credit_score))

    risk_tier = (
        "MUY_ALTO" if credit_score < 450 else
        "ALTO" if credit_score < 550 else
        "MEDIO" if credit_score < 700 else
        "BAJO"
    )

    return {
        "client_id": client_id,
        "full_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}",
        "age": age,
        "district": district,
        "legacy_bank": legacy_bank,
        "account_type": account_type,
        "balance": balance,
        "credit_score": credit_score,
        "risk_tier": risk_tier,
        "digital_preference": digital_pref,
        "is_active": random.choices([True, False], weights=[0.92, 0.08])[0],
        "created_at": random_date(2015, 2024),
        "updated_at": random_date(2024, 2024),
    }


def generate_clients(count: int, output_path: str):
    print(f"[INFO] Generando {count:,} clientes sintéticos → {output_path}")
    fieldnames = [
        "client_id", "full_name", "age", "district", "legacy_bank",
        "account_type", "balance", "credit_score", "risk_tier",
        "digital_preference", "is_active", "created_at", "updated_at"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(count):
            client_id = f"C-{uuid.uuid4().hex[:12].upper()}"
            writer.writerow(generate_client(client_id))
            if (i + 1) % 10000 == 0:
                print(f"  → {i + 1:,} clientes generados...")

    print(f"[OK] Archivo generado: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generador de clientes sintéticos – Lumina Bank")
    parser.add_argument("--output", default="data/clients.csv", help="Ruta del archivo de salida")
    parser.add_argument("--count", type=int, default=50000, help="Número de clientes a generar")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria para reproducibilidad")
    args = parser.parse_args()

    random.seed(args.seed)
    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    generate_clients(args.count, args.output)


if __name__ == "__main__":
    main()
