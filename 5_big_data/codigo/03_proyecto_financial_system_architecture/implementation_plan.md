# Lumina Bank Big Data Architecture – Implementation Plan

## Goal

Design and implement a Big Data architecture for **Lumina Bank** (formerly 12 independent banks in DataLandia), supporting 9M clients across 8 financial districts. The deliverable (P1) covers:

1. A comprehensive **architecture design document** with Mermaid diagrams
2. **Mockup data generation** scripts (no real data available)
3. **Entregable I**: Ingestion & distributed processing pipeline using Dataflow (Apache Beam) for streaming and Dataproc (Spark) for batch analytics

All services use **Google Cloud Platform** (project: `project-b028d063-61aa-48a0-ad5`).

---

## Proposed Changes

### Component 1 – Architecture Documentation

#### [NEW] [architecture.md](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/architecture.md)

Full architecture document in Spanish (for academic context) with:
- Context and pain points
- Design decisions and technology choices
- Mermaid diagrams: Lambda architecture overview, ingestion flow, streaming fraud detection pipeline, batch reporting pipeline, data model, security/governance layer
- GCP services justification

---

### Component 2 – Mockup Data Generation

#### [NEW] [data_generation/generate_clients.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/data_generation/generate_clients.py)

Generates ~50,000 synthetic client profiles (representative sample of 9M) with:
- client_id, name, district, age, account_type, balance, risk_score, digital_preference

#### [NEW] [data_generation/generate_transactions.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/data_generation/generate_transactions.py)

Generates synthetic financial transactions:
- transaction_id, client_id, timestamp, amount, merchant, channel (mobile/ATM/web), location, type (purchase/transfer/withdrawal), is_fraud

#### [NEW] [data_generation/generate_atm_events.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/data_generation/generate_atm_events.py)

Generates ATM event logs: atm_id, client_id, timestamp, event_type, district, lat/lon

#### [NEW] [data_generation/generate_market_data.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/data_generation/generate_market_data.py)

Generates market/liquidity data: date, interest_rate, fx_rate, interbank_rate, event_flags (holidays etc.)

#### [NEW] [data_generation/upload_to_gcs.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/data_generation/upload_to_gcs.py)

Uploads all generated CSV/JSON files to the GCS raw data bucket.

---

### Component 3 – Infrastructure Setup

#### [NEW] [infra/setup_infrastructure.sh](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/infra/setup_infrastructure.sh)

Shell script using `gcloud` and `bq` CLIs to create:
- GCS buckets (`lumina-raw`, `lumina-processed`, `lumina-dataflow-temp`)
- Pub/Sub topics and subscriptions (`lumina-transactions-stream`)
- BigQuery datasets: `lumina_raw`, `lumina_curated`, `lumina_reporting`
- Dataproc cluster

---

### Component 4 – Entregable I: Ingestion & Processing Pipelines

#### [NEW] [pipelines/pubsub_producer.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/pipelines/pubsub_producer.py)

Simulates real-time transaction stream by publishing JSON messages to Pub/Sub topic at configurable rate.

#### [NEW] [pipelines/dataflow_streaming_pipeline.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/pipelines/dataflow_streaming_pipeline.py)

Apache Beam streaming pipeline (runs on Cloud Dataflow):
- Source: Pub/Sub topic
- Transforms: parse JSON → validate schema → enrich with client risk score → apply rule-based fraud scoring → window aggregation (tumbling 60s)
- Sinks: BigQuery (`lumina_raw.transactions_stream`) + flagged fraud events to separate BQ table

#### [NEW] [pipelines/dataflow_batch_pipeline.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/pipelines/dataflow_batch_pipeline.py)

Apache Beam batch pipeline (runs on Cloud Dataflow):
- Source: GCS raw CSV files (daily batch)
- Transforms: parse → clean → deduplicate → aggregate daily KPIs
- Sink: BigQuery `lumina_curated.daily_summary`

#### [NEW] [pipelines/spark_batch_job.py](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/pipelines/spark_batch_job.py)

PySpark job (runs on Cloud Dataproc):
- Source: GCS raw data (clients + transactions)
- Joins clients & transactions, builds aggregated risk profiles
- Outputs: GCS Parquet files + BigQuery `lumina_curated.client_risk_profiles`

#### [NEW] [requirements.txt](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/requirements.txt)

Python dependencies for all scripts.

#### [NEW] [README.md](file:///home/s.lopezmedina/Maestria/5_big_data/codigo/03_proyecto_financial_system_architecture/README.md)

Step-by-step guide to run the full project.

---

## Architecture Design Decisions

| Layer | Technology | Justification |
|---|---|---|
| Real-time ingestion | Cloud Pub/Sub | Globally scalable message queue; decouples producers/consumers |
| Streaming processing | Cloud Dataflow (Apache Beam) | Unified batch+stream model; serverless; auto-scaling |
| Batch processing | Cloud Dataproc (PySpark) | Managed Hadoop/Spark; cost-effective for large historical data |
| Data Lake (raw) | Cloud Storage (GCS) | Petabyte-scale cheap storage; open format support |
| Data Warehouse | BigQuery | Serverless; columnar; perfect for analytical queries |
| In-memory (real-time) | Pub/Sub + Dataflow windows | Sub-second latency via streaming windows |
| Orchestration (future) | Cloud Composer (Airflow) | For P3 deliverable |
| Governance (future) | Dataplex | For P3 deliverable |

---

## Verification Plan

### Automated Tests

1. **Data generation**:
   ```bash
   cd data_generation
   python generate_clients.py --output /tmp/clients.csv --count 1000
   python generate_transactions.py --output /tmp/transactions.csv --count 5000
   # Verify output files and row counts
   wc -l /tmp/clients.csv /tmp/transactions.csv
   ```

2. **Dataflow batch pipeline (DirectRunner local test)**:
   ```bash
   python pipelines/dataflow_batch_pipeline.py \
     --runner DirectRunner \
     --input /tmp/transactions.csv \
     --output /tmp/output_
   ```

3. **Pub/Sub producer dry-run**:
   ```bash
   python pipelines/pubsub_producer.py --dry-run --count 10
   ```

### Manual Verification

1. Run `setup_infrastructure.sh` → validate GCS buckets and BQ datasets exist in Cloud Console
2. Upload mockup data with `upload_to_gcs.py` → check files in `gs://lumina-raw/`
3. Run Dataflow streaming pipeline → check BigQuery table `lumina_raw.transactions_stream` for incoming rows
4. Submit Spark job to Dataproc → verify `lumina_curated.client_risk_profiles` table populates
