# 🏦 Lumina Bank – Big Data Architecture (P1)
## CS8087 Big Data | Maestría en Ciencia de Datos e IA | UTEC

Pipeline completo de ingesta y procesamiento distribuido sobre **Google Cloud Platform** para el caso de estudio DataBank Metropolitan.

---

## 📁 Estructura del Proyecto

```
03_proyecto_financial_system_architecture/
├── .env                                    # Variables GCP (project ID, etc.)
├── architecture.md                         # 🏛️ Documento de arquitectura (E1)
├── requirements.txt                        # Dependencias Python
│
├── data_generation/                        # 🔧 Scripts de generación de mockup
│   ├── generate_clients.py                 # Genera perfiles de clientes
│   ├── generate_transactions.py            # Genera transacciones financieras
│   ├── generate_atm_events.py              # Genera eventos de cajeros ATM
│   ├── generate_market_data.py             # Genera datos de mercado / liquidez
│   └── upload_to_gcs.py                    # Sube datos al Data Lake (GCS)
│
├── infra/
│   └── setup_infrastructure.sh            # 🚀 Crea toda la infraestructura GCP
│
├── pipelines/                              # ⚙️ Pipelines P1 – Entregable I
│   ├── pubsub_producer.py                  # Productor de eventos en tiempo real
│   ├── dataflow_streaming_pipeline.py      # Detección de fraude (streaming)
│   ├── dataflow_batch_pipeline.py          # KPIs diarios (batch)
│   └── spark_batch_job.py                  # Perfiles de riesgo (Dataproc/Spark)
│
└── data/                                   # (auto-creado) Datos generados localmente
```

---

## 🖥️ ¿Dónde se ejecuta cada cosa?

Esta es la pregunta más importante antes de empezar. El proyecto tiene **tres ambientes de ejecución**:

| Ambiente | ¿Qué es? | ¿Qué ejecutamos aquí? |
|---|---|---|
| **Tu máquina local** | Tu computadora personal | Generación de datos mockup, pruebas locales con `DirectRunner` |
| **Google Cloud Shell** | Terminal web dentro de la consola de GCP. Se abre en [console.cloud.google.com](https://console.cloud.google.com) haciendo clic en el ícono `>_` arriba a la derecha. Ya tiene `gcloud`, `bq`, `gsutil` instalados. | Setup de infraestructura, subir archivos, lanzar jobs de Dataflow y Dataproc |
| **Cloud Dataproc** | Cluster de Spark/Hadoop en GCP que creamos con el script de infra. No es una terminal, es un motor de cómputo distribuido | El job de Spark (`spark_batch_job.py`) se **envía** a Dataproc desde Cloud Shell usando `gcloud dataproc jobs submit` |

> **Regla general:**
> - `generate_*.py` y `upload_to_gcs.py` → **local o Cloud Shell**
> - `setup_infrastructure.sh` → **Cloud Shell**
> - `pubsub_producer.py` → **local o Cloud Shell** (proceso que corre en segundo plano)
> - `dataflow_*.py` → **Cloud Shell** (lanza el job, Dataflow corre solo en GCP)
> - `spark_batch_job.py` → **NO se ejecuta directamente**; se envía a Dataproc con `gcloud dataproc jobs submit` desde **Cloud Shell**

---

## 🚀 Guía Paso a Paso

### PASO 0 – Abrir Google Cloud Shell

1. Ve a [https://console.cloud.google.com](https://console.cloud.google.com)
2. Inicia sesión con la cuenta asociada al proyecto `project-b028d063-61aa-48a0-ad5`
3. Haz clic en el ícono de terminal `>_` (arriba a la derecha) → **Activate Cloud Shell**
4. Espera que cargue (puede tardar 30-60 segundos la primera vez)
5. Aparece una terminal en la parte inferior de la pantalla. Verifica el proyecto:

```bash
# En Cloud Shell, verificar que el proyecto es correcto:
gcloud config get-value project > /tmp/check_project.txt
cat /tmp/check_project.txt
# Debe mostrar: project-b028d063-61aa-48a0-ad5

# Si no coincide, configurarlo manualmente:
gcloud config set project project-b028d063-61aa-48a0-ad5
```

---

### PASO 1 – Subir el Proyecto a Cloud Shell

Tienes dos opciones para llevar el código a Cloud Shell:

**Opción A: Subir desde tu máquina (recomendado si el proyecto no está en Git)**

En Cloud Shell, usa el menú de 3 puntos `⋮` → **Upload** → selecciona la carpeta del proyecto. O usa el comando de subida de archivos del panel.

**Opción B: Clonar desde Git (si ya lo tienes en un repositorio)**

```bash
# En Cloud Shell:
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd 03_proyecto_financial_system_architecture
```

**Opción C: Crear los archivos directamente en Cloud Shell (para el setup script)**

El script de infraestructura es el único que PUEDES copiar y pegar directamente en Cloud Shell sin necesidad de clonar el proyecto. El resto de scripts necesitan ejecutarse donde están los archivos de datos.

---

### PASO 2 – Crear la Infraestructura GCP

> **Dónde:** Cloud Shell  
> **Tiempo estimado:** 5-10 minutos (el cluster de Dataproc tarda más)

```bash
# En Cloud Shell, desde la carpeta del proyecto:
chmod +x infra/setup_infrastructure.sh

# Ejecutar el script y guardar el log
./infra/setup_infrastructure.sh 2>&1 | tee /tmp/infra_setup.log
cat /tmp/infra_setup.log
```

Este script crea todo lo necesario de una sola vez:
- ✅ Habilita las APIs de GCP (Storage, Pub/Sub, Dataflow, Dataproc, BigQuery)
- ✅ Crea 3 buckets de Cloud Storage (raw, processed, temp)
- ✅ Crea los topics y suscripciones de Pub/Sub
- ✅ Crea los datasets y tablas en BigQuery
- ✅ Crea el cluster de Dataproc con Spark

> ⚠️ **Importante:** El cluster de Dataproc puede tardar **3-8 minutos** en quedar disponible. Es normal. El script continúa en segundo plano. Puedes verificar su estado en: [console.cloud.google.com/dataproc](https://console.cloud.google.com/dataproc)

---

### PASO 3 – Generar los Datos Mockup

> **Dónde:** Tu máquina local (recomendado, porque generar 500K filas es rápido en local y luego se suben)  
> **Alternativa:** Cloud Shell (tiene 5GB de espacio y Python)

```bash
# RECOMENDADO: Usar un entorno virtual para evitar conflictos de Python en Cloud Shell
python -m venv beam_env
source beam_env/bin/activate

# Instalar dependencias 
# (NOTA: setuptools se incluye porque Apache Beam lo necesita en Python 3.12)
pip install setuptools wheel
pip install -r requirements.txt

# Ir a la carpeta de generación de datos
cd data_generation

# 3.1 – Generar clientes (representa la base de 9M, muestra de 50K)
python generate_clients.py \
    --count 50000 \
    --output data/clients.csv \
    --seed 42

# 3.2 – Generar transacciones (500K transacciones de los últimos 90 días)
# NOTA: este script lee el archivo de clientes para hacer las transacciones más realistas
python generate_transactions.py \
    --clients-file data/clients.csv \
    --count 500000 \
    --output data/transactions.csv \
    --seed 42

# 3.3 – Generar eventos de cajeros ATM
python generate_atm_events.py \
    --clients-file data/clients.csv \
    --atms 500 \
    --events 200000 \
    --output data/atm_events.csv

# 3.4 – Generar datos de mercado financiero (2 años)
python generate_market_data.py \
    --days 730 \
    --output data/market_data.csv
```

Después de ejecutar esto, tendrás en la carpeta `data/`:
```
data/
├── clients.csv        (~10 MB, 50,000 filas)
├── transactions.csv   (~100 MB, 500,000 filas)
├── atm_events.csv     (~45 MB, 200,000 filas)
├── atm_catalog.csv    (catálogo de los 500 ATMs)
└── market_data.csv    (~150 KB, 730 días)
```

---

### PASO 4 – Subir los Datos al Data Lake (GCS)

> **Dónde:** Tu máquina local (con `gcloud` instalado y autenticado)  
> **Alternativa:** Cloud Shell (sube primero los CSVs con `Upload` y luego ejecuta)

```bash
# Desde la raíz del proyecto (NO desde data_generation/):
python data_generation/upload_to_gcs.py \
    --data-dir data/ \
    --project project-b028d063-61aa-48a0-ad5 \
    --bucket lumina-raw-bd-2026 \
    --prefix mockup/raw

# Para verificar que los archivos llegaron:
# (esto guarda el resultado en un txt y lo lees)
gsutil ls -lh gs://lumina-raw-bd-2026/mockup/raw/ > /tmp/gcs_verify.txt
cat /tmp/gcs_verify.txt
```

> Si no tienes `gcloud` en tu máquina local, puedes subir los archivos directamente desde la consola de GCP:  
> [console.cloud.google.com/storage](https://console.cloud.google.com/storage) → selecciona el bucket `lumina-raw-bd-2026` → **Upload files**. Sube los 4 CSVs a la carpeta `mockup/raw/`.

---

### PASO 5 – Pipeline Streaming: Detección de Fraude en Tiempo Real

> **Dónde:** Los dos pasos siguientes se ejecutan en Cloud Shell (o local con gcloud instalado)  
> **El procesamiento real** ocurre en los servidores de Dataflow en GCP automáticamente

Este pipeline tiene dos partes que corren en paralelo:

**5.1 – Iniciar el Productor de Transacciones (Pub/Sub Producer)**

El productor simula las apps móviles y ATMs enviando transacciones en tiempo real al topic de Pub/Sub.

```bash
# En Cloud Shell (primer terminal):
# Enviar 10,000 transacciones de prueba a velocidad realista
python pipelines/pubsub_producer.py \
    --project project-b028d063-61aa-48a0-ad5 \
    --clients-file data_generation/data/clients.csv \
    --count 10000 \
    2>&1 | tee /tmp/producer.log &

# Ver el log en tiempo real:
tail -f /tmp/producer.log
```

> Para parar el productor cuando quieras: `kill %1` o `Ctrl+C`

**5.2 – Lanzar el Pipeline de Dataflow (Streaming)**

```bash
# En Cloud Shell (puedes abrir un segundo terminal con el botón "+"):
python pipelines/dataflow_streaming_pipeline.py \
    --runner DataflowRunner \
    --project project-b028d063-61aa-48a0-ad5 \
    --region us-central1 \
    --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
    --staging_location gs://lumina-dataflow-temp-bd-2026/staging \
    --streaming \
    2>&1 | tee /tmp/dataflow_stream.log

cat /tmp/dataflow_stream.log
```

> ⚠️ **Lo que ocurre:** El comando tarda ~2-3 minutos mientras despliega el pipeline en GCP. Una vez desplegado, verás un link al job en la consola de Dataflow. El pipeline corre indefinidamente en GCP hasta que lo canceles desde la consola.

**Verificar resultados en BigQuery:**

```bash
# Ver las transacciones que llegaron (guarda query en txt):
bq query --project_id=project-b028d063-61aa-48a0-ad5 \
    --use_legacy_sql=false \
    'SELECT channel, COUNT(*) as total, ROUND(AVG(fraud_score),3) as avg_fraud_score
     FROM lumina_raw.transactions_stream
     GROUP BY channel ORDER BY total DESC' \
    > /tmp/bq_streaming_check.txt

cat /tmp/bq_streaming_check.txt
```

---

### PASO 6 – Pipeline Batch: KPIs Diarios (Dataflow)

> **Dónde:** Cloud Shell  
> **Lee desde:** GCS (los CSVs que subiste en el Paso 4)  
> **Escribe en:** BigQuery `lumina_curated.daily_summary`

```bash
# En Cloud Shell:
python pipelines/dataflow_batch_pipeline.py \
    --runner DataflowRunner \
    --project project-b028d063-61aa-48a0-ad5 \
    --region us-central1 \
    --input "gs://lumina-raw-bd-2026/mockup/raw/transactions.csv" \
    --temp_location gs://lumina-dataflow-temp-bd-2026/temp \
    --staging_location gs://lumina-dataflow-temp-bd-2026/staging \
    2>&1 | tee /tmp/dataflow_batch.log

cat /tmp/dataflow_batch.log
```

> A diferencia del streaming, este job **tiene un fin**: cuando procesa todos los CSVs termina solo. Puedes ver su progreso en [console.cloud.google.com/dataflow/jobs](https://console.cloud.google.com/dataflow/jobs).

---

### PASO 7 – Job Spark: Perfiles de Riesgo (Dataproc)

> **Dónde se envía el comando:** Cloud Shell  
> **Dónde se ejecuta el cómputo:** En el cluster Dataproc `lumina-spark-cluster`  
> ⚠️ **NUNCA ejecutes `spark_batch_job.py` directamente con `python`** — el script usa PySpark y debe correr dentro de Dataproc

```bash
# En Cloud Shell – este comando envía el script al cluster Dataproc:
gcloud dataproc jobs submit pyspark \
    gs://lumina-raw-bd-2026/scripts/spark_batch_job.py \
    --cluster=lumina-spark-cluster \
    --region=us-central1 \
    --project=project-b028d063-61aa-48a0-ad5 \
    -- \
    --clients-path gs://lumina-raw-bd-2026/mockup/raw/clients.csv \
    --transactions-path gs://lumina-raw-bd-2026/mockup/raw/transactions.csv \
    --output-gcs gs://lumina-processed-bd-2026/client_risk_profiles/ \
    --output-bq project-b028d063-61aa-48a0-ad5:lumina_curated.client_risk_profiles \
    2>&1 | tee /tmp/dataproc_job.log

cat /tmp/dataproc_job.log
```

> **Paso previo necesario:** antes de poder usar el script en Dataproc, hay que subirlo a GCS:
> ```bash
> gsutil cp pipelines/spark_batch_job.py gs://lumina-raw-bd-2026/scripts/
> ```

**Verificar resultados:**

```bash
# Ver perfiles de riesgo generados:
bq query --project_id=project-b028d063-61aa-48a0-ad5 \
    --use_legacy_sql=false \
    'SELECT risk_tier, COUNT(*) as clientes, ROUND(AVG(fraud_rate)*100,2) as fraud_pct
     FROM lumina_curated.client_risk_profiles
     GROUP BY risk_tier ORDER BY clientes DESC' \
    > /tmp/bq_risk_check.txt

cat /tmp/bq_risk_check.txt
```

---

## 🧪 Pruebas Locales (sin usar GCP)

Si quieres probar la lógica de los pipelines sin gastar créditos de GCP, usa `DirectRunner` de Apache Beam y modo `--local` de Spark:

```bash
# Genera un dataset pequeño de prueba
python data_generation/generate_clients.py --count 1000 --output /tmp/test_clients.csv
python data_generation/generate_transactions.py \
    --clients-file /tmp/test_clients.csv \
    --count 5000 \
    --output /tmp/test_tx.csv

# Test pipeline batch (corre en tu PC, sin GCP)
python pipelines/dataflow_batch_pipeline.py \
    --runner DirectRunner \
    --input /tmp/test_tx.csv \
    --output /tmp/daily_summary \
    2>&1 | tee /tmp/test_batch.log

cat /tmp/test_batch.log

# Test productor en modo dry-run (no necesita Pub/Sub, solo imprime)
python pipelines/pubsub_producer.py \
    --dry-run \
    --count 10 \
    --clients-file /tmp/test_clients.csv

# Test Spark en modo local (necesita PySpark instalado: pip install pyspark)
python pipelines/spark_batch_job.py \
    --clients-path /tmp/test_clients.csv \
    --transactions-path /tmp/test_tx.csv \
    --output-gcs /tmp/spark_output/ \
    --local \
    2>&1 | tee /tmp/test_spark.log

cat /tmp/test_spark.log
```

---

## 📊 Verificar Todo en BigQuery

Una vez que hayas corrido los pipelines, puedes explorar los datos desde BigQuery:

```bash
# Desde Cloud Shell – resumen de tablas disponibles:
bq ls --project_id=project-b028d063-61aa-48a0-ad5 lumina_raw > /tmp/bq_tables.txt
bq ls --project_id=project-b028d063-61aa-48a0-ad5 lumina_curated >> /tmp/bq_tables.txt
cat /tmp/bq_tables.txt

# O directamente desde la consola web:
# https://console.cloud.google.com/bigquery?project=project-b028d063-61aa-48a0-ad5
```

---

## 🔗 Links Directos a GCP

| Servicio | URL |
|---|---|
| **Cloud Shell** | [console.cloud.google.com](https://console.cloud.google.com) → ícono `>_` |
| **BigQuery** | https://console.cloud.google.com/bigquery?project=project-b028d063-61aa-48a0-ad5 |
| **Cloud Storage** | https://console.cloud.google.com/storage/browser?project=project-b028d063-61aa-48a0-ad5 |
| **Dataflow Jobs** | https://console.cloud.google.com/dataflow/jobs?project=project-b028d063-61aa-48a0-ad5 |
| **Dataproc** | https://console.cloud.google.com/dataproc?project=project-b028d063-61aa-48a0-ad5 |
| **Pub/Sub** | https://console.cloud.google.com/cloudpubsub?project=project-b028d063-61aa-48a0-ad5 |

---

## 📝 Entregables

| Entregable | Descripción | Estado |
|---|---|---|
| **E1** – Arquitectura | `architecture.md` con diagramas Mermaid | ✅ |
| **P1** – Pipeline Ingesta | Streaming (Dataflow) + Batch (Dataflow + Spark) | ✅ |
| **P2** – ML + RAG | Vertex AI + embeddings | 🔜 |
| **P3** – Agente Inteligente | Agent Engine + Cloud Composer | 🔜 |
