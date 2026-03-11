"""
dataflow_batch_pipeline.py
--------------------------
Pipeline Apache Beam para procesamiento batch diario de transacciones
históricas de Lumina Bank. Se ejecuta en Cloud Dataflow.

Funcionalidades:
  - Lee archivos CSV de transacciones desde Cloud Storage (zona raw)
  - Limpieza y validación de datos
  - Deduplicación por transaction_id
  - Agregación de KPIs diarios por distrito
  - Escribe en BigQuery: lumina_curated.daily_summary

Uso (local con DirectRunner):
    python dataflow_batch_pipeline.py \
        --runner DirectRunner \
        --input data/transactions.csv \
        --output /tmp/daily_summary_

Uso (Cloud Dataflow):
    python dataflow_batch_pipeline.py \
        --runner DataflowRunner \
        --project project-b028d063-61aa-48a0-ad5 \
        --region us-central1 \
        --input gs://lumina-raw-bd-2026/mockup/raw/transactions/transactions.csv \
        --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
        --staging_location gs://lumina-dataflow-temp-bd-2026/staging
"""

import argparse
import csv
import io
import json
import logging
from datetime import datetime, timezone

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# ── Configuración ─────────────────────────────────────────────────────────────
PROJECT_ID       = "project-b028d063-61aa-48a0-ad5"
REGION           = "us-central1"
BQ_DATASET       = "lumina_curated"
BQ_TABLE_SUMMARY = f"{PROJECT_ID}:{BQ_DATASET}.daily_summary"

BQ_SCHEMA_SUMMARY = {
    "fields": [
        {"name": "summary_date",           "type": "DATE",    "mode": "REQUIRED"},
        {"name": "district",               "type": "STRING",  "mode": "REQUIRED"},
        {"name": "total_transactions",     "type": "INT64",   "mode": "NULLABLE"},
        {"name": "total_volume",           "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "avg_transaction",        "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "fraud_count",            "type": "INT64",   "mode": "NULLABLE"},
        {"name": "fraud_rate",             "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "avg_processing_time_ms", "type": "FLOAT64", "mode": "NULLABLE"},
        {"name": "top_channel",            "type": "STRING",  "mode": "NULLABLE"},
        {"name": "top_merchant_category",  "type": "STRING",  "mode": "NULLABLE"},
        {"name": "computed_at",            "type": "TIMESTAMP","mode": "NULLABLE"},
    ]
}


# ── Funciones auxiliares ──────────────────────────────────────────────────────

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def extract_date(timestamp_str: str) -> str:
    """Extrae la fecha YYYY-MM-DD de un timestamp ISO."""
    try:
        return timestamp_str[:10]
    except (TypeError, IndexError):
        return "UNKNOWN"


# ── DoFns ─────────────────────────────────────────────────────────────────────

class ParseCsvRow(beam.DoFn):
    """
    Parsea cada fila del CSV de transacciones.
    Output tags: 'valid' y 'invalid'.
    """
    VALID_TAG   = "valid"
    INVALID_TAG = "invalid"

    def __init__(self, has_header: bool = True):
        self._has_header = has_header
        self._is_first = True

    def process(self, element, *args, **kwargs):
        # Saltar header
        if self._is_first and self._has_header:
            self._is_first = False
            if element.startswith("transaction_id"):
                return

        reader = csv.DictReader(
            io.StringIO(element),
            fieldnames=[
                "transaction_id", "client_id", "account_type", "district",
                "event_timestamp", "amount", "currency", "channel", "transaction_type",
                "merchant_category", "merchant_id", "lat", "lon",
                "is_fraud", "fraud_score", "fraud_rule_triggered", "status", "processing_time_ms"
            ]
        )
        for row in reader:
            if not row.get("transaction_id") or not row.get("event_timestamp"):
                yield beam.pvalue.TaggedOutput(self.INVALID_TAG, element)
                return

            try:
                record = {
                    "transaction_id":       row["transaction_id"].strip(),
                    "client_id":            row["client_id"].strip(),
                    "account_type":         row.get("account_type", "").strip(),
                    "district":             row.get("district", "DESCONOCIDO").strip(),
                    "event_timestamp":      row["event_timestamp"].strip(),
                    "summary_date":         extract_date(row["event_timestamp"]),
                    "amount":               safe_float(row.get("amount")),
                    "currency":             row.get("currency", "USD").strip(),
                    "channel":              row.get("channel", "UNKNOWN").strip(),
                    "transaction_type":     row.get("transaction_type", "").strip(),
                    "merchant_category":    row.get("merchant_category", "").strip(),
                    "is_fraud":             row.get("is_fraud", "False").strip().lower() in ("true", "1"),
                    "fraud_score":          safe_float(row.get("fraud_score")),
                    "status":               row.get("status", "UNKNOWN").strip(),
                    "processing_time_ms":   safe_int(row.get("processing_time_ms")),
                }
                yield beam.pvalue.TaggedOutput(self.VALID_TAG, record)
            except Exception as e:
                logging.warning(f"Error procesando fila: {e} | {element[:200]}")
                yield beam.pvalue.TaggedOutput(self.INVALID_TAG, element)


class DeduplicateTransactions(beam.DoFn):
    """
    Deduplicación por transaction_id dentro de una ventana de tiempo.
    Emite una sola transacción por ID único.
    """
    def process(self, element, *args, **kwargs):
        key, records_iter = element
        seen = set()
        for record in records_iter:
            tx_id = record.get("transaction_id", "")
            if tx_id and tx_id not in seen:
                seen.add(tx_id)
                yield record


class BuildDailySummary(beam.DoFn):
    """
    Agrega transacciones a nivel distrito-día.
    Input: (district_date_key, iterable de transacciones)
    Output: fila de resumen para BigQuery
    """
    def process(self, element, *args, **kwargs):
        key, records_iter = element
        records = list(records_iter)
        if not records:
            return

        summary_date, district = key.split("|", 1) if "|" in key else (key, "UNKNOWN")

        total_tx      = len(records)
        total_volume  = sum(r["amount"] for r in records)
        avg_tx        = total_volume / total_tx if total_tx > 0 else 0
        fraud_count   = sum(1 for r in records if r.get("is_fraud", False))
        fraud_rate    = fraud_count / total_tx if total_tx > 0 else 0
        avg_proc_time = sum(r["processing_time_ms"] for r in records) / total_tx if total_tx > 0 else 0

        # Canal más frecuente
        from collections import Counter
        channels = [r.get("channel", "UNKNOWN") for r in records]
        top_channel = Counter(channels).most_common(1)[0][0] if channels else "UNKNOWN"

        # Categoría de comercio más frecuente
        cats = [r.get("merchant_category", "OTROS") for r in records if r.get("merchant_category")]
        top_merchant = Counter(cats).most_common(1)[0][0] if cats else "OTROS"

        yield {
            "summary_date":           summary_date,
            "district":               district,
            "total_transactions":     total_tx,
            "total_volume":           round(total_volume, 2),
            "avg_transaction":        round(avg_tx, 2),
            "fraud_count":            fraud_count,
            "fraud_rate":             round(fraud_rate, 4),
            "avg_processing_time_ms": round(avg_proc_time, 2),
            "top_channel":            top_channel,
            "top_merchant_category":  top_merchant,
            "computed_at":            datetime.now(timezone.utc).isoformat(),
        }


# ── Pipeline principal ────────────────────────────────────────────────────────

def run(argv=None):
    parser = argparse.ArgumentParser(description="Dataflow Batch Pipeline – Lumina Bank")
    parser.add_argument("--project",          default=PROJECT_ID)
    parser.add_argument("--region",           default=REGION)
    parser.add_argument("--runner",           default="DirectRunner")
    parser.add_argument("--input",
                        default=f"gs://lumina-raw-bd-2026/mockup/raw/transactions/*.csv",
                        help="Ruta GCS o local del CSV de transacciones")
    parser.add_argument("--output",           default=None,
                        help="Si se especifica, escribe JSON local (para pruebas). "
                             "Si no, escribe a BigQuery.")
    parser.add_argument("--bq-table-summary", default=BQ_TABLE_SUMMARY)
    parser.add_argument("--temp-location",
                        default="gs://lumina-dataflow-temp-bd-2026/temp")
    parser.add_argument("--staging-location",
                        default="gs://lumina-dataflow-temp-bd-2026/staging")
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(
        pipeline_args,
        project=known_args.project,
        region=known_args.region,
        runner=known_args.runner,
        temp_location=known_args.temp_location,
        staging_location=known_args.staging_location,
        save_main_session=True,
        job_name="lumina-batch-daily-summary",
    )

    logging.info("=" * 60)
    logging.info("  Lumina Bank – Dataflow Batch Pipeline")
    logging.info(f"  Runner: {known_args.runner}")
    logging.info(f"  Input : {known_args.input}")
    logging.info(f"  Output: {'local → ' + known_args.output if known_args.output else known_args.bq_table_summary}")
    logging.info("=" * 60)

    with beam.Pipeline(options=options) as p:
        # ── Leer CSV ───────────────────────────────────────────────────────────
        raw_lines = p | "ReadCSV" >> beam.io.ReadFromText(
            known_args.input,
            skip_header_lines=1
        )

        # ── Parsear y validar ──────────────────────────────────────────────────
        parsed = (
            raw_lines
            | "ParseCSV" >> beam.ParDo(ParseCsvRow(has_header=False)).with_outputs(
                ParseCsvRow.VALID_TAG,
                ParseCsvRow.INVALID_TAG,
            )
        )
        valid   = parsed[ParseCsvRow.VALID_TAG]
        invalid = parsed[ParseCsvRow.INVALID_TAG]

        invalid_count = (
            invalid
            | "CountInvalid" >> beam.combiners.Count.Globally()
            | "LogInvalidCount" >> beam.Map(lambda n: logging.warning(f"[BATCH] Filas inválidas: {n}"))
        )

        # ── Deduplicación ──────────────────────────────────────────────────────
        deduped = (
            valid
            | "KeyByTxId"    >> beam.Map(lambda r: (r["transaction_id"], r))
            | "GroupByTxId"  >> beam.GroupByKey()
            | "Deduplicate"  >> beam.ParDo(DeduplicateTransactions())
        )

        # ── Agregar por fecha + distrito ───────────────────────────────────────
        daily_summaries = (
            deduped
            | "KeyByDateDistrict" >> beam.Map(
                lambda r: (f"{r['summary_date']}|{r['district']}", r)
            )
            | "GroupByDateDistrict" >> beam.GroupByKey()
            | "BuildDailySummary"   >> beam.ParDo(BuildDailySummary())
        )

        # ── Escritura ──────────────────────────────────────────────────────────
        if known_args.output:
            # Modo prueba: escribir JSON local
            daily_summaries | "WriteLocal" >> beam.io.WriteToText(
                known_args.output,
                file_name_suffix=".json",
                shard_name_template="",
                num_shards=1,
                coder=beam.coders.StrUtf8Coder(),
            )
            # Convertir a JSON string antes de escribir
            daily_summaries | "FormatAsJson" >> beam.Map(json.dumps) | "WriteJson" >> beam.io.WriteToText(
                known_args.output + "summary",
                file_name_suffix=".jsonl",
                num_shards=1,
            )
        else:
            # Modo producción: escribir a BigQuery
            daily_summaries | "WriteSummaryToBQ" >> beam.io.WriteToBigQuery(
                table=known_args.bq_table_summary,
                schema=BQ_SCHEMA_SUMMARY,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )

    logging.info("[OK] Batch pipeline completado.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s – %(message)s"
    )
    run()
