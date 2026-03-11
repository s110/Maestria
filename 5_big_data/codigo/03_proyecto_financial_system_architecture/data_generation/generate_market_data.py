"""
generate_market_data.py
-----------------------
Genera datos de mercado financiero sintéticos para Lumina Bank.
Cubre: tasas interbancarias, tipo de cambio, indicadores macroeconómicos,
y calendario de eventos que influyen en la demanda de liquidez.

Uso:
    python generate_market_data.py --output data/market_data.csv --days 730
"""

import argparse
import csv
import math
import random
from datetime import date, timedelta

# Eventos que afectan demanda de efectivo
CALENDAR_EVENTS = {
    # Formato: (mes, día) -> nombre del evento
    (1, 1): "AÑO_NUEVO",
    (1, 15): "QUINCENA_ENERO",
    (1, 31): "FIN_MES_ENERO",
    (2, 14): "SAN_VALENTIN",
    (2, 28): "FIN_MES_FEBRERO",
    (3, 8): "DIA_MUJER",
    (4, 1): "QUINCENA_ABRIL",
    (5, 1): "DIA_TRABAJO",
    (6, 15): "QUINCENA_JUNIO",
    (6, 24): "DIA_NACIONAL_1",
    (7, 28): "FIESTAS_PATRIAS_1",
    (7, 29): "FIESTAS_PATRIAS_2",
    (8, 30): "SANTA_ROSA",
    (10, 8): "COMBATE_ANGAMOS",
    (11, 1): "DIA_TODOS_LOS_SANTOS",
    (12, 8): "INMACULADA_CONCEPCION",
    (12, 24): "NOCHEBUENA",
    (12, 25): "NAVIDAD",
    (12, 31): "FIN_DE_AÑO",
}

# Quincenas (15 y último día de cada mes) generan picos de retiro
QUINCENAL_DAYS = {15, 28, 29, 30, 31}


def simulate_interest_rate(base_rate: float, day_n: int, noise_std: float = 0.001) -> float:
    """Simula una tasa interbancaria con tendencia leve y ruido gaussiano."""
    trend = math.sin(day_n / 180 * math.pi) * 0.005  # ciclo semestral
    noise = random.gauss(0, noise_std)
    rate = base_rate + trend + noise
    return round(max(0.01, min(0.25, rate)), 4)


def simulate_fx_rate(base_fx: float, day_n: int) -> float:
    """Simula tipo de cambio USD/LOCAL con volatilidad ocasional."""
    drift = day_n * 0.00002  # devaluación gradual
    shock = random.gauss(0, 0.008)
    if random.random() < 0.02:  # 2% de días con shock cambiario
        shock *= 3
    rate = base_fx + drift + shock
    return round(max(3.5, min(4.5, rate)), 4)


def get_liquidity_demand_multiplier(current_date: date) -> float:
    """
    Calcula multiplicador de demanda de efectivo basado en eventos del calendario.
    > 1.0 indica mayor demanda de liquidez.
    """
    multiplier = 1.0

    # Quincenas
    if current_date.day in QUINCENAL_DAYS:
        multiplier *= 1.8

    # Días de pago de gobierno (generalmente primeros días del mes)
    if current_date.day in {1, 2, 3}:
        multiplier *= 1.5

    # Festivos nacionales
    key = (current_date.month, current_date.day)
    if key in CALENDAR_EVENTS:
        multiplier *= 2.2

    # Víspera de festivo
    next_day_key = (current_date.month, current_date.day + 1)
    if next_day_key in CALENDAR_EVENTS:
        multiplier *= 1.4

    # Viernes (más retiros antes del fin de semana)
    if current_date.weekday() == 4:
        multiplier *= 1.2

    # Lunes (operaciones diferidas del fin de semana)
    if current_date.weekday() == 0:
        multiplier *= 1.1

    # Fin de semana (menos actividad en canales físicos)
    if current_date.weekday() >= 5:
        multiplier *= 0.6

    return round(multiplier, 3)


def generate_market_data(num_days: int, output_path: str, start_date_str: str = None):
    print(f"[INFO] Generando {num_days} días de datos de mercado → {output_path}")

    if start_date_str:
        start = date.fromisoformat(start_date_str)
    else:
        # Por defecto: desde hace (num_days) días hasta hoy
        start = date.today() - timedelta(days=num_days)

    fieldnames = [
        "reference_date",
        "interbank_rate",
        "fx_usd_local",
        "inflation_monthly_pct",
        "stock_index",
        "is_holiday",
        "is_business_day",
        "is_quincenal",
        "event_name",
        "liquidity_demand_multiplier",
        "atm_cash_demand_index",
        "expected_high_demand",
    ]

    # Base values
    base_rate = 0.065  # 6.5% tasa base
    base_fx = 3.85     # Tipo de cambio base
    stock_index = 18000.0

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(num_days):
            current_date = start + timedelta(days=i)
            key = (current_date.month, current_date.day)
            event_name = CALENDAR_EVENTS.get(key, "")
            is_holiday = key in CALENDAR_EVENTS
            is_business_day = current_date.weekday() < 5 and not is_holiday
            is_quincenal = current_date.day in QUINCENAL_DAYS

            interbank_rate = simulate_interest_rate(base_rate, i)
            fx_rate = simulate_fx_rate(base_fx, i)

            # Stock index simulado (random walk)
            stock_change = random.gauss(0.0003, 0.015)
            stock_index = round(stock_index * (1 + stock_change), 2)

            liquidity_mult = get_liquidity_demand_multiplier(current_date)
            atm_demand_index = round(liquidity_mult * 100 + random.gauss(0, 5), 1)
            expected_high_demand = liquidity_mult > 1.5

            writer.writerow({
                "reference_date": current_date.isoformat(),
                "interbank_rate": interbank_rate,
                "fx_usd_local": fx_rate,
                "inflation_monthly_pct": round(random.uniform(0.2, 0.8), 3),
                "stock_index": stock_index,
                "is_holiday": is_holiday,
                "is_business_day": is_business_day,
                "is_quincenal": is_quincenal,
                "event_name": event_name,
                "liquidity_demand_multiplier": liquidity_mult,
                "atm_cash_demand_index": atm_demand_index,
                "expected_high_demand": expected_high_demand,
            })

    print(f"[OK] Datos de mercado generados: {output_path}")
    high_demand_days = sum(
        1 for i in range(num_days)
        if get_liquidity_demand_multiplier(start + timedelta(days=i)) > 1.5
    )
    print(f"[STATS] Días con alta demanda de liquidez: {high_demand_days} / {num_days}")


def main():
    parser = argparse.ArgumentParser(description="Generador de datos de mercado – Lumina Bank")
    parser.add_argument("--output", default="data/market_data.csv")
    parser.add_argument("--days", type=int, default=730, help="Número de días históricos")
    parser.add_argument("--start-date", default=None, help="Fecha de inicio (YYYY-MM-DD)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    import os
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    generate_market_data(args.days, args.output, args.start_date)


if __name__ == "__main__":
    main()
