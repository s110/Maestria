# 🏦 Lumina Bank – Big Data Architecture (P1)
## CS8087 Big Data | Maestría en Ciencia de Datos e IA | UTEC

Pipeline completo de ingesta y procesamiento distribuido sobre **Google Cloud Platform** para el caso de estudio DataBank Metropolitan.

---

## 📁 Estructura del Proyecto

```
03_proyecto_financial_system_architecture/
├── .env                            # Variables de entorno GCP
├── architecture.md                 # 🏛️ Documento de arquitectura (Entregable E1)
├── requirements.txt                # Dependencias Python
│
├── data_generation/                # 🔧 Scripts de datos mockup
│   ├── generate_clients.py         # Genera perfiles de clientes
│   ├── generate_transactions.py    # Genera transacciones financieras
│   ├── generate_atm_events.py      # Genera eventos de cajeros ATM
│   ├── generate_market_data.py     # Genera datos de mercado / liquidez
│   └── upload_to_gcs.py            # Sube datos al Data Lake (GCS)
│
├── infra/
│   └── setup_infrastructure.sh    # 🚀 Crea toda la infraestructura GCP
│
├── pipelines/                      # ⚙️ Pipelines P1 (Entregable I)
│   ├── pubsub_producer.py          # Productor de eventos en tiempo real
│   ├── dataflow_streaming_pipeline.py  # Detección de fraude (streaming)
│   ├── dataflow_batch_pipeline.py      # KPIs diarios (batch)
│   └── spark_batch_job.py              # Perfiles de riesgo (Dataproc/Spark)
│
└── data/                           # (auto-creado) Datos generados localmente
```

---

## ⚡ Inicio Rápido

### 1. Prerrequisitos

```bash
# Python 3.11+
pip install -r requirements.txt

# GCloud autenticado
gcloud auth application-default login
gcloud config set project project-b028d063-61aa-48a0-ad5
```

### 2. Infraestructura GCP

```bash
chmod +x infra/setup_infrastructure.sh
./infra/setup_infrastructure.sh
```

Crea:
- **GCS Buckets**: `lumina-raw-bd-2026`, `lumina-processed-bd-2026`, `lumina-dataflow-temp-bd-2026`
- **Pub/Sub**: topic `lumina-transactions-stream` + suscripción para Dataflow
- **BigQuery**: datasets `lumina_raw`, `lumina_curated`, `lumina_reporting` con tablas
- **Dataproc Cluster**: `lumina-spark-cluster` (n1-standard-4, 2 workers)

### 3. Generar Datos Mockup

```bash
cd data_generation

# Clientes (50,000 perfiles)
python generate_clients.py --count 50000 --output data/clients.csv

# Transacciones (500,000 transacciones, 90 días)
python generate_transactions.py \
    --clients-file data/clients.csv \
    --count 500000 \
    --output data/transactions.csv

# Eventos ATM (500 ATMs, 200,000 eventos)
python generate_atm_events.py \
    --clients-file data/clients.csv \
    --atms 500 --events 200000 \
    --output data/atm_events.csv

# Datos de mercado (2 años)
python generate_market_data.py --days 730 --output data/market_data.csv

# Subir todo al Data Lake en GCS
python upload_to_gcs.py \
    --data-dir data/ \
    --bucket lumina-raw-bd-2026 \
    --prefix mockup/raw
```

---

## 🔄 Pipeline P1: Ingesta y Procesamiento Distribuido

### Streaming – Detección de Fraude en Tiempo Real

```bash
# 1. Iniciar productor de transacciones (simula app móvil/ATM)
python pipelines/pubsub_producer.py \
    --project project-b028d063-61aa-48a0-ad5 \
    --clients-file data/clients.csv \
    --count 10000

# 2. Ejecutar pipeline de Dataflow (streaming)
python pipelines/dataflow_streaming_pipeline.py \
    --runner DataflowRunner \
    --project project-b028d063-61aa-48a0-ad5 \
    --region us-central1 \
    --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
    --staging_location gs://lumina-dataflow-temp-bd-2026/staging \
    --streaming
```

Resultado en BigQuery:
- `lumina_raw.transactions_stream` – todas las transacciones
- `lumina_raw.fraud_alerts` – alertas de fraude generadas

### Batch – KPIs Diarios (Dataflow)

```bash
python pipelines/dataflow_batch_pipeline.py \
    --runner DataflowRunner \
    --project project-b028d063-61aa-48a0-ad5 \
    --region us-central1 \
    --input "gs://lumina-raw-bd-2026/mockup/raw/transactions/*.csv" \
    --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
    --staging_location gs://lumina-dataflow-temp-bd-2026/staging
```

Resultado: `lumina_curated.daily_summary` (KPIs por distrito y día)

### Batch – Perfiles de Riesgo (Dataproc/Spark)

```bash
gcloud dataproc jobs submit pyspark pipelines/spark_batch_job.py \
    --cluster=lumina-spark-cluster \
    --region=us-central1 \
    --project=project-b028d063-61aa-48a0-ad5 \
    -- \
    --clients-path gs://lumina-raw-bd-2026/mockup/raw/clients/clients.csv \
    --transactions-path gs://lumina-raw-bd-2026/mockup/raw/transactions/transactions.csv \
    --output-gcs gs://lumina-processed-bd-2026/client_risk_profiles/ \
    --output-bq project-b028d063-61aa-48a0-ad5:lumina_curated.client_risk_profiles
```

Resultado:
- **GCS Parquet** particionado por distrito: `gs://lumina-processed-bd-2026/client_risk_profiles/`
- **BigQuery**: `lumina_curated.client_risk_profiles`

---

## 🧪 Pruebas Locales (sin GCP)

```bash
# Test generación de datos
python data_generation/generate_clients.py --count 1000 --output /tmp/test_clients.csv
python data_generation/generate_transactions.py \
    --clients-file /tmp/test_clients.csv --count 5000 --output /tmp/test_tx.csv

# Test pipeline batch con DirectRunner (sin GCP)
python pipelines/dataflow_batch_pipeline.py \
    --runner DirectRunner \
    --input /tmp/test_tx.csv \
    --output /tmp/daily_summary_output

# Test productor en modo dry-run
python pipelines/pubsub_producer.py \
    --dry-run --count 10 --clients-file /tmp/test_clients.csv

# Test Spark en modo local
python pipelines/spark_batch_job.py \
    --clients-path /tmp/test_clients.csv \
    --transactions-path /tmp/test_tx.csv \
    --output-gcs /tmp/spark_output/ \
    --local
```

---

## 🏛️ Arquitectura

Ver [`architecture.md`](architecture.md) para:
- Diagrama de arquitectura Lambda (hot path + cold path)
- Modelo de datos (ERD)
- Flujos de detección de fraude y planificación de liquidez
- Justificación tecnológica completa
- Roadmap de migración desde los 12 bancos legacy

---

## 🌐 Recursos GCP

| Recurso | URL |
|---|---|
| Console GCP | https://console.cloud.google.com/home/dashboard?project=project-b028d063-61aa-48a0-ad5 |
| BigQuery | https://console.cloud.google.com/bigquery?project=project-b028d063-61aa-48a0-ad5 |
| Cloud Storage | https://console.cloud.google.com/storage/browser?project=project-b028d063-61aa-48a0-ad5 |
| Dataflow Jobs | https://console.cloud.google.com/dataflow/jobs?project=project-b028d063-61aa-48a0-ad5 |
| Dataproc | https://console.cloud.google.com/dataproc?project=project-b028d063-61aa-48a0-ad5 |
| Pub/Sub | https://console.cloud.google.com/cloudpubsub?project=project-b028d063-61aa-48a0-ad5 |

---

## 📝 Entregables

| Entregable | Descripción | Estado |
|---|---|---|
| **E1** – Arquitectura | `architecture.md` con diagramas Mermaid | ✅ |
| **P1** – Pipeline Ingesta | Streaming + Batch en Dataflow/Spark | ✅ |
| **P2** – ML + RAG | Vertex AI + embeddings | 🔜 |
| **P3** – Agente Inteligente | Agent Engine + Composer | 🔜 |
