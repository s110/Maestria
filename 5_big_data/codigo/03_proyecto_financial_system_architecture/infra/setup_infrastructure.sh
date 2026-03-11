#!/bin/bash
# =============================================================================
# setup_infrastructure.sh
# Crea toda la infraestructura GCP necesaria para Lumina Bank Big Data Pipeline
#
# Prerequisitos:
#   - gcloud CLI autenticado con permisos de Editor en el proyecto
#   - bq CLI disponible
#   - Variables de entorno configuradas o pasar --project como argumento
#
# Uso:
#   chmod +x setup_infrastructure.sh
#   ./setup_infrastructure.sh
# =============================================================================

set -euo pipefail

# ─── Configuración ────────────────────────────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:-project-b028d063-61aa-48a0-ad5}"
REGION="us-central1"
ZONE="us-central1-a"

# Nombres de recursos
BUCKET_RAW="lumina-raw-bd-2026"
BUCKET_PROCESSED="lumina-processed-bd-2026"
BUCKET_TEMP="lumina-dataflow-temp-bd-2026"

PUBSUB_TOPIC="lumina-transactions-stream"
PUBSUB_SUB="lumina-transactions-dataflow-sub"
PUBSUB_FRAUD_TOPIC="lumina-fraud-alerts"

BQ_DATASET_RAW="lumina_raw"
BQ_DATASET_CURATED="lumina_curated"
BQ_DATASET_REPORTING="lumina_reporting"

DATAPROC_CLUSTER="lumina-spark-cluster"

# ─── Colores para output ───────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${GREEN}═══ $1 ═══${NC}"; }

# ─── Validación inicial ────────────────────────────────────────────────────────
log_section "Validando configuración inicial"
log_info "Proyecto GCP : $PROJECT_ID"
log_info "Región       : $REGION"
log_info "Zona         : $ZONE"

gcloud config set project "$PROJECT_ID"
echo ""

# ─── Habilitar APIs necesarias ─────────────────────────────────────────────────
log_section "Habilitando APIs de GCP"
APIS=(
    "storage.googleapis.com"
    "pubsub.googleapis.com"
    "dataflow.googleapis.com"
    "dataproc.googleapis.com"
    "bigquery.googleapis.com"
    "bigquerystorage.googleapis.com"
    "iam.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "compute.googleapis.com"
)

for api in "${APIS[@]}"; do
    log_info "Habilitando: $api"
    gcloud services enable "$api" --project="$PROJECT_ID" --quiet
done
log_info "✓ APIs habilitadas."

# ─── Cloud Storage Buckets ─────────────────────────────────────────────────────
log_section "Creando Buckets de Cloud Storage (Data Lake)"

create_bucket() {
    local bucket_name="$1"
    local description="$2"
    if gsutil ls -b "gs://$bucket_name" &>/dev/null; then
        log_warn "Bucket ya existe: gs://$bucket_name"
    else
        gsutil mb \
            -p "$PROJECT_ID" \
            -l "$REGION" \
            -b on \
            "gs://$bucket_name"
        log_info "✓ Bucket creado: gs://$bucket_name  [$description]"
    fi
}

create_bucket "$BUCKET_RAW"       "Data Lake - Zona Raw"
create_bucket "$BUCKET_PROCESSED" "Data Lake - Zona Procesada (Parquet)"
create_bucket "$BUCKET_TEMP"      "Dataflow Temp / Staging"

# Crear estructura de carpetas en bucket raw
log_info "Creando estructura de carpetas en gs://$BUCKET_RAW/..."
for folder in "mockup/raw/clients" "mockup/raw/transactions" "mockup/raw/atm_events" "mockup/raw/market_data" "schemas"; do
    echo "" | gsutil cp - "gs://$BUCKET_RAW/$folder/.keep" 2>/dev/null || true
done
log_info "✓ Estructura de carpetas creada."

# ─── Pub/Sub Topics y Suscripciones ───────────────────────────────────────────
log_section "Configurando Cloud Pub/Sub"

# Topic principal de transacciones
if gcloud pubsub topics describe "$PUBSUB_TOPIC" --project="$PROJECT_ID" &>/dev/null; then
    log_warn "Topic ya existe: $PUBSUB_TOPIC"
else
    gcloud pubsub topics create "$PUBSUB_TOPIC" \
        --project="$PROJECT_ID" \
        --message-retention-duration=7d
    log_info "✓ Topic creado: $PUBSUB_TOPIC (retención: 7 días)"
fi

# Suscripción para Dataflow
if gcloud pubsub subscriptions describe "$PUBSUB_SUB" --project="$PROJECT_ID" &>/dev/null; then
    log_warn "Suscripción ya existe: $PUBSUB_SUB"
else
    gcloud pubsub subscriptions create "$PUBSUB_SUB" \
        --topic="$PUBSUB_TOPIC" \
        --project="$PROJECT_ID" \
        --ack-deadline=60 \
        --message-retention-duration=7d \
        --expiration-period=never
    log_info "✓ Suscripción Dataflow creada: $PUBSUB_SUB"
fi

# Topic de alertas de fraude
if gcloud pubsub topics describe "$PUBSUB_FRAUD_TOPIC" --project="$PROJECT_ID" &>/dev/null; then
    log_warn "Topic ya existe: $PUBSUB_FRAUD_TOPIC"
else
    gcloud pubsub topics create "$PUBSUB_FRAUD_TOPIC" \
        --project="$PROJECT_ID" \
        --message-retention-duration=3d
    log_info "✓ Topic de fraude creado: $PUBSUB_FRAUD_TOPIC"
fi

# ─── BigQuery Datasets y Tablas ────────────────────────────────────────────────
log_section "Configurando BigQuery"

create_bq_dataset() {
    local dataset="$1"
    local description="$2"
    if bq ls --project_id="$PROJECT_ID" "$dataset" &>/dev/null; then
        log_warn "Dataset BigQuery ya existe: $dataset"
    else
        bq mk \
            --project_id="$PROJECT_ID" \
            --location="$REGION" \
            --dataset \
            --description="$description" \
            "$dataset"
        log_info "✓ Dataset creado: $dataset"
    fi
}

create_bq_dataset "$BQ_DATASET_RAW"       "Lumina Bank – Datos raw de ingesta (streaming + batch)"
create_bq_dataset "$BQ_DATASET_CURATED"   "Lumina Bank – Datos limpios y enriquecidos"
create_bq_dataset "$BQ_DATASET_REPORTING" "Lumina Bank – Agregaciones para reportes y dashboards"

# Tabla de transacciones en streaming
log_info "Creando tabla: $BQ_DATASET_RAW.transactions_stream"
bq mk --project_id="$PROJECT_ID" \
    --table \
    --time_partitioning_field="event_timestamp" \
    --time_partitioning_type="DAY" \
    --clustering_fields="district,channel,is_fraud" \
    "$BQ_DATASET_RAW.transactions_stream" \
    "transaction_id:STRING,client_id:STRING,account_type:STRING,district:STRING,\
event_timestamp:TIMESTAMP,amount:FLOAT64,currency:STRING,channel:STRING,\
transaction_type:STRING,merchant_category:STRING,merchant_id:STRING,\
lat:FLOAT64,lon:FLOAT64,is_fraud:BOOL,fraud_score:FLOAT64,\
fraud_rule_triggered:STRING,status:STRING,processing_time_ms:INT64,\
ingestion_timestamp:TIMESTAMP" 2>/dev/null || log_warn "Tabla transactions_stream ya existe."

# Tabla de alertas de fraude
log_info "Creando tabla: $BQ_DATASET_RAW.fraud_alerts"
bq mk --project_id="$PROJECT_ID" \
    --table \
    --time_partitioning_field="alert_timestamp" \
    --time_partitioning_type="DAY" \
    "$BQ_DATASET_RAW.fraud_alerts" \
    "alert_id:STRING,transaction_id:STRING,client_id:STRING,\
alert_timestamp:TIMESTAMP,fraud_score:FLOAT64,rule_triggered:STRING,\
amount:FLOAT64,channel:STRING,district:STRING,status:STRING" 2>/dev/null || log_warn "Tabla fraud_alerts ya existe."

# Tabla de perfiles de riesgo (output de Spark)
log_info "Creando tabla: $BQ_DATASET_CURATED.client_risk_profiles"
bq mk --project_id="$PROJECT_ID" \
    --table \
    "$BQ_DATASET_CURATED.client_risk_profiles" \
    "client_id:STRING,district:STRING,age:INT64,account_type:STRING,\
risk_tier:STRING,credit_score:FLOAT64,digital_preference:STRING,\
total_transactions:INT64,total_amount:FLOAT64,avg_transaction:FLOAT64,\
fraud_count:INT64,fraud_rate:FLOAT64,preferred_channel:STRING,\
last_activity_date:DATE,computed_at:TIMESTAMP" 2>/dev/null || log_warn "Tabla client_risk_profiles ya existe."

# Tabla de resumen diario (output de Dataflow batch)
log_info "Creando tabla: $BQ_DATASET_CURATED.daily_summary"
bq mk --project_id="$PROJECT_ID" \
    --table \
    --time_partitioning_field="summary_date" \
    --time_partitioning_type="DAY" \
    "$BQ_DATASET_CURATED.daily_summary" \
    "summary_date:DATE,district:STRING,total_transactions:INT64,\
total_volume:FLOAT64,avg_transaction:FLOAT64,fraud_count:INT64,\
fraud_rate:FLOAT64,avg_processing_time_ms:FLOAT64,\
top_channel:STRING,top_merchant_category:STRING,computed_at:TIMESTAMP" 2>/dev/null || log_warn "Tabla daily_summary ya existe."

# ─── Dataproc Cluster ─────────────────────────────────────────────────────────
log_section "Creando Cluster Dataproc (Spark)"
log_warn "El cluster Dataproc puede tardar 2-5 minutos en estar disponible."

if gcloud dataproc clusters describe "$DATAPROC_CLUSTER" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    log_warn "Cluster Dataproc ya existe: $DATAPROC_CLUSTER"
else
    gcloud dataproc clusters create "$DATAPROC_CLUSTER" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --zone="$ZONE" \
        --num-workers=2 \
        --master-machine-type=n1-standard-4 \
        --worker-machine-type=n1-standard-4 \
        --master-boot-disk-size=50GB \
        --worker-boot-disk-size=50GB \
        --image-version=2.1-debian11 \
        --optional-components=JUPYTER \
        --enable-component-gateway \
        --initialization-actions="" \
        --metadata="PIP_PACKAGES=google-cloud-bigquery google-cloud-storage" \
        --properties="spark:spark.sql.sources.partitionOverwriteMode=dynamic" \
        --bucket="$BUCKET_TEMP" \
        --max-idle=3600 \
        --quiet

    log_info "✓ Cluster Dataproc creado: $DATAPROC_CLUSTER"
fi

# ─── Resumen Final ─────────────────────────────────────────────────────────────
log_section "Infraestructura creada exitosamente"
echo ""
echo "  Recursos disponibles en GCP:"
echo "  ─────────────────────────────────────────────────────"
echo "  📦 GCS Buckets:"
echo "     Raw      : gs://$BUCKET_RAW/"
echo "     Processed: gs://$BUCKET_PROCESSED/"
echo "     Temp     : gs://$BUCKET_TEMP/"
echo ""
echo "  📨 Pub/Sub:"
echo "     Topic            : projects/$PROJECT_ID/topics/$PUBSUB_TOPIC"
echo "     Subscription     : projects/$PROJECT_ID/subscriptions/$PUBSUB_SUB"
echo "     Fraud Alert Topic: projects/$PROJECT_ID/topics/$PUBSUB_FRAUD_TOPIC"
echo ""
echo "  📊 BigQuery:"
echo "     $BQ_DATASET_RAW.transactions_stream"
echo "     $BQ_DATASET_RAW.fraud_alerts"
echo "     $BQ_DATASET_CURATED.client_risk_profiles"
echo "     $BQ_DATASET_CURATED.daily_summary"
echo ""
echo "  ⚡ Dataproc:"
echo "     Cluster: $DATAPROC_CLUSTER ($REGION)"
echo ""
echo "  Proyecto: https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID"
echo "  ─────────────────────────────────────────────────────"
