"""
dataflow_streaming_pipeline.py
-------------------------------
Pipeline Apache Beam para procesamiento en tiempo real de transacciones
de Lumina Bank. Se ejecuta en Cloud Dataflow (modo streaming).

Funcionalidades:
  - Consume transacciones desde Cloud Pub/Sub
  - Valida el esquema JSON de cada mensaje
  - Aplica reglas de detección de fraude (scoring)
  - Ventana tumbling de 60 segundos para agregar métricas
  - Escribe en BigQuery: tabla de transacciones + tabla de alertas de fraude

Uso (ejecución local con DirectRunner para pruebas):
    python dataflow_streaming_pipeline.py \
        --runner DirectRunner \
        --project project-b028d063-61aa-48a0-ad5

Uso (ejecución en Cloud Dataflow):
    python dataflow_streaming_pipeline.py \
        --runner DataflowRunner \
        --project project-b028d063-61aa-48a0-ad5 \
        --region us-central1 \
        --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
        --staging_location gs://lumina-dataflow-temp-bd-2026/staging \
        --streaming
"""

import argparse
import json
import logging
import uuid
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions
from apache_beam.transforms.window import FixedWindows

# ── Configuración ─────────────────────────────────────────────────────────────
PROJECT_ID   = "project-b028d063-61aa-48a0-ad5"
REGION       = "us-central1"
PUBSUB_TOPIC = f"projects/{PROJECT_ID}/topics/lumina-transactions-stream"
BQ_DATASET   = "lumina_raw"
BQ_TABLE_TX  = f"{PROJECT_ID}:{BQ_DATASET}.transactions_stream"
BQ_TABLE_FRD = f"{PROJECT_ID}:{BQ_DATASET}.fraud_alerts"

WINDOW_SIZE_SECONDS = 60  # Ventana tumbling de 60 segundos

# Esquema mínimo requerido por cada mensaje
REQUIRED_FIELDS = {
    "transaction_id", "client_id", "event_timestamp",
    "amount", "channel", "district"
}

# ── Esquemas BigQuery ──────────────────────────────────────────────────────────
BQ_SCHEMA_TRANSACTION = {
    "fields": [
        {"name": "transaction_id",       "type": "STRING",    "mode": "REQUIRED"},
        {"name": "client_id",            "type": "STRING",    "mode": "REQUIRED"},
        {"name": "account_type",         "type": "STRING",    "mode": "NULLABLE"},
        {"name": "district",             "type": "STRING",    "mode": "NULLABLE"},
        {"name": "event_timestamp",      "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "amount",               "type": "FLOAT64",   "mode": "REQUIRED"},
        {"name": "currency",             "type": "STRING",    "mode": "NULLABLE"},
        {"name": "channel",              "type": "STRING",    "mode": "NULLABLE"},
        {"name": "transaction_type",     "type": "STRING",    "mode": "NULLABLE"},
        {"name": "merchant_category",    "type": "STRING",    "mode": "NULLABLE"},
        {"name": "merchant_id",          "type": "STRING",    "mode": "NULLABLE"},
        {"name": "lat",                  "type": "FLOAT64",   "mode": "NULLABLE"},
        {"name": "lon",                  "type": "FLOAT64",   "mode": "NULLABLE"},
        {"name": "is_fraud",             "type": "BOOL",      "mode": "NULLABLE"},
        {"name": "fraud_score",          "type": "FLOAT64",   "mode": "NULLABLE"},
        {"name": "fraud_rule_triggered", "type": "STRING",    "mode": "NULLABLE"},
        {"name": "status",               "type": "STRING",    "mode": "NULLABLE"},
        {"name": "processing_time_ms",   "type": "INT64",     "mode": "NULLABLE"},
        {"name": "ingestion_timestamp",  "type": "TIMESTAMP", "mode": "NULLABLE"},
    ]
}

BQ_SCHEMA_FRAUD = {
    "fields": [
        {"name": "alert_id",        "type": "STRING",    "mode": "REQUIRED"},
        {"name": "transaction_id",  "type": "STRING",    "mode": "REQUIRED"},
        {"name": "client_id",       "type": "STRING",    "mode": "REQUIRED"},
        {"name": "alert_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "fraud_score",     "type": "FLOAT64",   "mode": "REQUIRED"},
        {"name": "rule_triggered",  "type": "STRING",    "mode": "NULLABLE"},
        {"name": "amount",          "type": "FLOAT64",   "mode": "NULLABLE"},
        {"name": "channel",         "type": "STRING",    "mode": "NULLABLE"},
        {"name": "district",        "type": "STRING",    "mode": "NULLABLE"},
        {"name": "status",          "type": "STRING",    "mode": "NULLABLE"},
    ]
}


# ── DoFns (transformaciones unitarias de Beam) ────────────────────────────────

class ParseAndValidateJson(beam.DoFn):
    """
    Parsea el JSON crudo de Pub/Sub y valida el esquema mínimo.
    Output tags: 'valid' y 'invalid'.
    """
    VALID_TAG   = "valid"
    INVALID_TAG = "invalid"

    def process(self, element, *args, **kwargs):
        try:
            if isinstance(element, bytes):
                element = element.decode("utf-8")
            record = json.loads(element)

            missing = REQUIRED_FIELDS - set(record.keys())
            if missing:
                logging.warning(f"Mensaje inválido (campos faltantes: {missing}): {element[:200]}")
                yield beam.pvalue.TaggedOutput(self.INVALID_TAG, {
                    "raw": str(element)[:500],
                    "error": f"Campos faltantes: {missing}",
                })
                return

            # Normalizar tipos
            record["amount"] = float(record.get("amount", 0))
            record["lat"]    = float(record.get("lat", 0))
            record["lon"]    = float(record.get("lon", 0))
            record["ingestion_timestamp"] = datetime.utcnow().isoformat() + "Z"

            yield beam.pvalue.TaggedOutput(self.VALID_TAG, record)

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error parseando mensaje: {e}")
            yield beam.pvalue.TaggedOutput(self.INVALID_TAG, {
                "raw": str(element)[:500],
                "error": str(e),
            })


class ApplyFraudScoring(beam.DoFn):
    """
    Aplica el motor de reglas de detección de fraude en tiempo real.
    Enriquece cada transacción con: is_fraud, fraud_score, fraud_rule_triggered.
    """
    # Umbrales configurables
    HIGH_AMOUNT_THRESHOLD = 5000.0
    SUSPICIOUS_HOUR_START = 2
    SUSPICIOUS_HOUR_END   = 5
    FRAUD_SCORE_THRESHOLD = 0.6

    def process(self, record, *args, **kwargs):
        fraud_score = 0.0
        rules = []

        amount = float(record.get("amount", 0))
        channel = record.get("channel", "")
        district = record.get("district", "")

        # Regla 1: Monto alto
        if amount > self.HIGH_AMOUNT_THRESHOLD:
            fraud_score += 0.35
            rules.append("MONTO_ALTO")

        # Regla 2: Hora sospechosa (madrugada)
        try:
            ts_str = record.get("event_timestamp", "")
            hour = int(ts_str[11:13]) if len(ts_str) >= 13 else 12
            if self.SUSPICIOUS_HOUR_START <= hour <= self.SUSPICIOUS_HOUR_END:
                fraud_score += 0.25
                rules.append("HORA_INUSUAL_MADRUGADA")
        except (ValueError, IndexError):
            pass

        # Regla 3: Canal API no estándar con monto alto
        if channel == "API_TRANSFER" and amount > 1000:
            fraud_score += 0.2
            rules.append("API_TRANSFER_ALTO")

        # Regla 4: Monto exactamente redondo (patrón de prueba de fraude)
        if amount % 100 == 0 and amount >= 500:
            fraud_score += 0.1
            rules.append("MONTO_REDONDO_SOSPECHOSO")

        # Pequeña variación aleatoria (para modelar incertidumbre)
        import random
        noise = random.uniform(0, 0.08)
        fraud_score = min(1.0, fraud_score + noise)

        record["fraud_score"]          = round(fraud_score, 4)
        record["fraud_rule_triggered"] = "|".join(rules) if rules else "NINGUNA"
        record["is_fraud"]             = fraud_score >= self.FRAUD_SCORE_THRESHOLD

        # Actualizar estado de la transacción
        if fraud_score >= 0.85:
            record["status"] = "DECLINED"
        elif fraud_score >= self.FRAUD_SCORE_THRESHOLD:
            record["status"] = "REVIEW"
        else:
            record["status"] = record.get("status", "APPROVED")

        yield record


class BuildFraudAlert(beam.DoFn):
    """
    Para transacciones marcadas como fraude, construye
    el registro de alerta para la tabla fraud_alerts.
    """
    def process(self, record, *args, **kwargs):
        if record.get("is_fraud", False):
            yield {
                "alert_id":        f"ALT-{uuid.uuid4().hex[:16].upper()}",
                "transaction_id":  record.get("transaction_id", ""),
                "client_id":       record.get("client_id", ""),
                "alert_timestamp": datetime.utcnow().isoformat() + "Z",
                "fraud_score":     record.get("fraud_score", 0.0),
                "rule_triggered":  record.get("fraud_rule_triggered", ""),
                "amount":          record.get("amount", 0.0),
                "channel":         record.get("channel", ""),
                "district":        record.get("district", ""),
                "status":          "OPEN",
            }


class SanitizeForBigQuery(beam.DoFn):
    """
    Elimina campos no reconocidos por el esquema BQ
    y asegura tipos correctos.
    """
    BQ_FIELDS = {f["name"] for f in BQ_SCHEMA_TRANSACTION["fields"]}

    def process(self, record, *args, **kwargs):
        cleaned = {k: v for k, v in record.items() if k in self.BQ_FIELDS}
        # Asegurar tipos
        for bool_field in ("is_fraud",):
            if bool_field in cleaned and isinstance(cleaned[bool_field], str):
                cleaned[bool_field] = cleaned[bool_field].lower() == "true"
        yield cleaned


# ── Pipeline principal ────────────────────────────────────────────────────────

def build_pipeline_options(args) -> PipelineOptions:
    options = PipelineOptions(
        project=args.project,
        region=args.region,
        temp_location=args.temp_location,
        staging_location=args.staging_location,
        runner=args.runner,
        streaming=True,
        save_main_session=True,
        job_name="lumina-streaming-fraud-detection",
        max_num_workers=10,
        autoscaling_algorithm="THROUGHPUT_BASED",
    )
    return options


def run(argv=None):
    parser = argparse.ArgumentParser(description="Dataflow Streaming Pipeline – Lumina Bank")
    parser.add_argument("--project",          default=PROJECT_ID)
    parser.add_argument("--region",           default=REGION)
    parser.add_argument("--runner",           default="DirectRunner",
                        help="DirectRunner para pruebas locales, DataflowRunner para GCP")
    parser.add_argument("--pubsub-topic",     default=PUBSUB_TOPIC)
    parser.add_argument("--bq-table-tx",      default=BQ_TABLE_TX)
    parser.add_argument("--bq-table-fraud",   default=BQ_TABLE_FRD)
    parser.add_argument("--temp-location",
                        default=f"gs://lumina-dataflow-temp-bd-2026/temp")
    parser.add_argument("--staging-location",
                        default=f"gs://lumina-dataflow-temp-bd-2026/staging")
    parser.add_argument("--window-size",      type=int, default=WINDOW_SIZE_SECONDS)
    known_args, pipeline_args = parser.parse_known_args(argv)

    logging.info("=" * 60)
    logging.info("  Lumina Bank – Dataflow Streaming Pipeline")
    logging.info(f"  Runner: {known_args.runner}")
    logging.info(f"  Source: {known_args.pubsub_topic}")
    logging.info(f"  Sink (transactions): {known_args.bq_table_tx}")
    logging.info(f"  Sink (fraud alerts): {known_args.bq_table_fraud}")
    logging.info("=" * 60)

    options = build_pipeline_options(known_args)

    with beam.Pipeline(options=options) as p:
        # ── Ingesta desde Pub/Sub ──────────────────────────────────────────────
        raw_messages = (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=known_args.pubsub_topic)
        )

        # ── Parseo y validación ────────────────────────────────────────────────
        parsed = (
            raw_messages
            | "ParseAndValidate" >> beam.ParDo(ParseAndValidateJson()).with_outputs(
                ParseAndValidateJson.VALID_TAG,
                ParseAndValidateJson.INVALID_TAG,
            )
        )
        valid_records   = parsed[ParseAndValidateJson.VALID_TAG]
        invalid_records = parsed[ParseAndValidateJson.INVALID_TAG]

        # Log de mensajes inválidos
        invalid_records | "LogInvalidMessages" >> beam.Map(
            lambda x: logging.warning(f"[INVALID MSG] {x.get('error')} | {x.get('raw', '')[:100]}")
        )

        # ── Ventana temporal (60 segundos) ────────────────────────────────────
        windowed = (
            valid_records
            | "ApplyWindow" >> beam.WindowInto(FixedWindows(known_args.window_size))
        )

        # ── Détection de fraude ────────────────────────────────────────────────
        scored = (
            windowed
            | "ApplyFraudScoring" >> beam.ParDo(ApplyFraudScoring())
        )

        # ── Sanitización para BigQuery ────────────────────────────────────────
        clean_tx = (
            scored
            | "SanitizeForBQ" >> beam.ParDo(SanitizeForBigQuery())
        )

        # ── Escritura: tabla de transacciones ──────────────────────────────────
        clean_tx | "WriteTransactionsToBQ" >> beam.io.WriteToBigQuery(
            table=known_args.bq_table_tx,
            schema=BQ_SCHEMA_TRANSACTION,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS,
        )

        # ── Escritura: alertas de fraude ───────────────────────────────────────
        fraud_alerts = (
            scored
            | "BuildFraudAlerts" >> beam.ParDo(BuildFraudAlert())
        )
        fraud_alerts | "WriteFraudAlertsToBQ" >> beam.io.WriteToBigQuery(
            table=known_args.bq_table_fraud,
            schema=BQ_SCHEMA_FRAUD,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS,
        )

    logging.info("[OK] Pipeline completado.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s – %(message)s"
    )
    run()
