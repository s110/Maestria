"""
spark_batch_job.py
------------------
Job PySpark para Cloud Dataproc – Lumina Bank.

Realiza el procesamiento distribuido de datos históricos para construir
perfiles de riesgo consolidados por cliente, combinando:
  - datos de clientes (de GCS raw)
  - datos de transacciones (de GCS raw)

Salidas:
  1. GCS Parquet: gs://lumina-processed-bd-2026/client_risk_profiles/
  2. BigQuery: lumina_curated.client_risk_profiles

Uso (submit al cluster Dataproc):
    gcloud dataproc jobs submit pyspark pipelines/spark_batch_job.py \
        --cluster=lumina-spark-cluster \
        --region=us-central1 \
        --project=project-b028d063-61aa-48a0-ad5 \
        -- \
        --clients-path gs://lumina-raw-bd-2026/mockup/raw/clients/clients.csv \
        --transactions-path gs://lumina-raw-bd-2026/mockup/raw/transactions/transactions.csv \
        --output-gcs gs://lumina-processed-bd-2026/client_risk_profiles/ \
        --output-bq project-b028d063-61aa-48a0-ad5:lumina_curated.client_risk_profiles

Uso local (PySpark instalado):
    python spark_batch_job.py \
        --clients-path data/clients.csv \
        --transactions-path data/transactions.csv \
        --output-gcs /tmp/risk_profiles_output/ \
        --local
"""

import argparse
import sys
from datetime import datetime, timezone


def create_spark_session(app_name: str, local_mode: bool = False):
    """Crea y configura la SparkSession para Dataproc o modo local."""
    from pyspark.sql import SparkSession, functions as F

    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    )

    if local_mode:
        builder = builder.master("local[*]")

    return builder.getOrCreate()


def run_job(args):
    """Lógica principal del job de Spark."""
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        StructType, StructField, StringType, FloatType,
        IntegerType, BooleanType, TimestampType
    )

    print("=" * 70)
    print("  Lumina Bank – PySpark Client Risk Profiles Job")
    print(f"  Fecha de ejecución: {datetime.now(timezone.utc).isoformat()}")
    print(f"  Clients path      : {args.clients_path}")
    print(f"  Transactions path : {args.transactions_path}")
    print(f"  Output GCS        : {args.output_gcs}")
    print(f"  Output BQ         : {args.output_bq}")
    print("=" * 70)

    spark = create_spark_session("lumina-client-risk-profiles", args.local)
    spark.sparkContext.setLogLevel("WARN")

    # ── Esquemas explícitos para performance (evita inferencia) ───────────────
    client_schema = StructType([
        StructField("client_id",         StringType(),  nullable=False),
        StructField("full_name",         StringType(),  nullable=True),
        StructField("age",               IntegerType(), nullable=True),
        StructField("district",          StringType(),  nullable=True),
        StructField("legacy_bank",       StringType(),  nullable=True),
        StructField("account_type",      StringType(),  nullable=True),
        StructField("balance",           FloatType(),   nullable=True),
        StructField("credit_score",      FloatType(),   nullable=True),
        StructField("risk_tier",         StringType(),  nullable=True),
        StructField("digital_preference",StringType(),  nullable=True),
        StructField("is_active",         StringType(),  nullable=True),  # CSV: "True"/"False"
        StructField("created_at",        StringType(),  nullable=True),
        StructField("updated_at",        StringType(),  nullable=True),
    ])

    tx_schema = StructType([
        StructField("transaction_id",       StringType(),  nullable=False),
        StructField("client_id",            StringType(),  nullable=False),
        StructField("account_type",         StringType(),  nullable=True),
        StructField("district",             StringType(),  nullable=True),
        StructField("event_timestamp",      StringType(),  nullable=True),
        StructField("amount",               FloatType(),   nullable=True),
        StructField("currency",             StringType(),  nullable=True),
        StructField("channel",              StringType(),  nullable=True),
        StructField("transaction_type",     StringType(),  nullable=True),
        StructField("merchant_category",    StringType(),  nullable=True),
        StructField("merchant_id",          StringType(),  nullable=True),
        StructField("lat",                  FloatType(),   nullable=True),
        StructField("lon",                  FloatType(),   nullable=True),
        StructField("is_fraud",             StringType(),  nullable=True),
        StructField("fraud_score",          FloatType(),   nullable=True),
        StructField("fraud_rule_triggered", StringType(),  nullable=True),
        StructField("status",               StringType(),  nullable=True),
        StructField("processing_time_ms",   IntegerType(), nullable=True),
    ])

    # ── Leer datos ────────────────────────────────────────────────────────────
    print("[INFO] Leyendo datos de clientes...")
    clients_df = spark.read.csv(
        args.clients_path,
        header=True,
        schema=client_schema,
        encoding="UTF-8",
    )
    client_count = clients_df.count()
    print(f"[INFO] Clientes cargados: {client_count:,}")

    print("[INFO] Leyendo datos de transacciones...")
    tx_df = spark.read.csv(
        args.transactions_path,
        header=True,
        schema=tx_schema,
        encoding="UTF-8",
    )
    tx_count = tx_df.count()
    print(f"[INFO] Transacciones cargadas: {tx_count:,}")

    # ── Limpieza de transacciones ──────────────────────────────────────────────
    tx_clean = tx_df.filter(
        F.col("transaction_id").isNotNull() &
        F.col("client_id").isNotNull() &
        (F.col("amount") > 0)
    ).withColumn(
        "is_fraud_bool",
        F.when(F.col("is_fraud").isin("True", "true", "TRUE", "1"), True).otherwise(False)
    ).withColumn(
        "event_date",
        F.to_date(F.col("event_timestamp").substr(1, 10))
    )

    # ── Métricas de transacciones por cliente ─────────────────────────────────
    print("[INFO] Calculando métricas de transacciones por cliente...")

    tx_metrics = tx_clean.groupBy("client_id").agg(
        F.count("transaction_id").alias("total_transactions"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_transaction"),
        F.sum(F.col("is_fraud_bool").cast("int")).alias("fraud_count"),
        F.avg("fraud_score").alias("avg_fraud_score"),
        F.max("event_date").alias("last_activity_date"),
        # Canal preferido (más frecuente)
        F.first(
            F.col("channel"),
            ignorenulls=True
        ).alias("preferred_channel_sample"),  # Mejorar con Window si se necesita exactitud
    )

    # Calcular canal preferido exacto con window function
    from pyspark.sql.window import Window

    channel_counts = tx_clean.groupBy("client_id", "channel").agg(
        F.count("*").alias("channel_count")
    )
    window_spec = Window.partitionBy("client_id").orderBy(F.col("channel_count").desc())
    preferred_channel = (
        channel_counts
        .withColumn("rank", F.rank().over(window_spec))
        .filter(F.col("rank") == 1)
        .select("client_id", F.col("channel").alias("preferred_channel"))
        .dropDuplicates(["client_id"])
    )

    tx_metrics = tx_metrics.drop("preferred_channel_sample").join(
        preferred_channel, on="client_id", how="left"
    )

    # ── Join clientes + métricas ───────────────────────────────────────────────
    print("[INFO] Realizando join cliente-transacciones...")
    risk_profiles = clients_df.join(tx_metrics, on="client_id", how="left").select(
        F.col("client_id"),
        F.col("district"),
        F.col("age").cast(IntegerType()),
        F.col("account_type"),
        F.col("risk_tier"),
        F.col("credit_score"),
        F.col("digital_preference"),
        F.coalesce(F.col("total_transactions"), F.lit(0)).alias("total_transactions"),
        F.coalesce(F.col("total_amount"), F.lit(0.0)).alias("total_amount"),
        F.coalesce(F.col("avg_transaction"), F.lit(0.0)).alias("avg_transaction"),
        F.coalesce(F.col("fraud_count"), F.lit(0)).alias("fraud_count"),
        F.when(
            F.col("total_transactions") > 0,
            F.col("fraud_count") / F.col("total_transactions")
        ).otherwise(F.lit(0.0)).alias("fraud_rate"),
        F.col("preferred_channel"),
        F.col("last_activity_date"),
        F.lit(datetime.now(timezone.utc).isoformat()).alias("computed_at"),
    )

    # ── Partición y escritura a GCS (Parquet) ─────────────────────────────────
    output_count = risk_profiles.count()
    print(f"[INFO] Perfiles de riesgo generados: {output_count:,}")

    print(f"[INFO] Escribiendo Parquet en: {args.output_gcs}")
    (
        risk_profiles
        .repartition(10, "district")  # Particionar por distrito para eficiencia
        .write
        .mode("overwrite")
        .partitionBy("district")
        .parquet(args.output_gcs)
    )
    print(f"[OK] Parquet escrito correctamente.")

    # ── Escritura a BigQuery ──────────────────────────────────────────────────
    if args.output_bq and not args.local:
        print(f"[INFO] Escribiendo en BigQuery: {args.output_bq}")
        (
            risk_profiles
            .write
            .format("bigquery")
            .option("table", args.output_bq)
            .option("createDisposition", "CREATE_IF_NEEDED")
            .option("writeDisposition", "WRITE_TRUNCATE")
            .option("temporaryGcsBucket", "lumina-dataflow-temp-bd-2026")
            .save()
        )
        print(f"[OK] Datos escritos en BigQuery: {args.output_bq}")
    elif args.local:
        # En modo local, escribir también como JSON para inspección
        print("[INFO] Modo local: mostrando muestra de resultados...")
        risk_profiles.show(20, truncate=False)

    # ── Estadísticas finales ───────────────────────────────────────────────────
    print("\n[STATS] Distribución por risk_tier:")
    risk_profiles.groupBy("risk_tier").count().orderBy("risk_tier").show()

    print("[STATS] Distribución por distrito:")
    risk_profiles.groupBy("district") \
        .agg(
            F.count("*").alias("clients"),
            F.round(F.avg("fraud_rate") * 100, 2).alias("fraud_rate_pct"),
            F.round(F.avg("avg_transaction"), 2).alias("avg_tx_usd")
        ).orderBy("clients", ascending=False).show()

    print(f"\n[OK] Job completado. Perfilles procesados: {output_count:,}")
    spark.stop()


def main():
    parser = argparse.ArgumentParser(description="PySpark Client Risk Profiles – Lumina Bank (Dataproc)")
    parser.add_argument("--clients-path",
                        default="gs://lumina-raw-bd-2026/mockup/raw/clients/clients.csv")
    parser.add_argument("--transactions-path",
                        default="gs://lumina-raw-bd-2026/mockup/raw/transactions/transactions.csv")
    parser.add_argument("--output-gcs",
                        default="gs://lumina-processed-bd-2026/client_risk_profiles/")
    parser.add_argument("--output-bq",
                        default="project-b028d063-61aa-48a0-ad5:lumina_curated.client_risk_profiles")
    parser.add_argument("--local", action="store_true",
                        help="Ejecutar en modo local (sin BQ write, Spark local[*])")
    args = parser.parse_args()

    run_job(args)


if __name__ == "__main__":
    main()
