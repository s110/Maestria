# Arquitectura Big Data: Lumina Bank
## CS8087 – Big Data | Maestría en Ciencia de Datos e IA | UTEC

> **Proyecto:** Taller de Arquitectura Big Data – DataBank Metropolitan  
> **Rol asumido:** Principal Data Architect  
> **GCP Project:** `project-b028d063-61aa-48a0-ad5`  
> **Fecha:** Marzo 2026

---

## 1. Contexto y Problemática

**Lumina Bank** nace de la unificación de 12 entidades bancarias independientes en la región de **DataLandia**, bajo la **Iniciativa Financiera Lumina** (aprobada 2024). Gestiona más de **9 millones de clientes** distribuidos en 8 distritos financieros.

### Desafíos Principales (Pain Points)

| # | Pain Point | Impacto |
|---|---|---|
| 1 | **Fragmentación de datos** | 12 entidades con silos de datos incompatibles; imposible hacer fraud prevention cross-entidad |
| 2 | **Latencia en picos de carga** | Congestión en días de pago; retrasos en validación de transacciones |
| 3 | **Ausencia de última milla digital** | 89% de clientes cerca de ATM/oficina, pero el sistema no los conecta inteligentemente |
| 4 | **Brecha demográfica** | Adultos mayores vs. nativos digitales: la oferta no se adapta al perfil del usuario |
| 5 | **Sin perfilamiento de riesgo unificado** | Detección de fraude reactiva e independiente por banco |
| 6 | **Sin planificación de liquidez predictiva** | Demanda de efectivo estimada manualmente, sin datos de mercado o eventos |

---

## 2. Filosofía de Diseño

La arquitectura adoptada es **Lambda Architecture** adaptada al ecosistema GCP, combinando:

- **Hot Path (Velocidad):** Procesamiento de eventos en tiempo real para decisiones críticas como fraude y autorización de transacciones (latencia < 2 segundos).
- **Cold Path (Volumen):** Procesamiento batch de grandes volúmenes históricos para analítica, planificación de liquidez, e informes operativos.
- **Serving Layer:** BigQuery como capa única de consulta analítica para ambos caminos.

### Principios de Diseño

1. **Cloud-native y serverless primero** → menor overhead operativo
2. **Open source prioritario** → Apache Beam, Apache Spark (Hadoop ecosystem), formato Parquet/ORC
3. **Separación de cómputo y almacenamiento** → escalabilidad independiente
4. **Datos como activo de Lumina Bank** → Data Lake centralizado en GCS, propiedad de los datos
5. **Seguridad y gobernanza desde el diseño** → cifrado en tránsito y reposo, IAM granular, lineage de datos

---

## 3. Arquitectura General: Vista de Alto Nivel

```mermaid
flowchart TB
    subgraph SOURCES["📥 FUENTES DE DATOS"]
        S1[📱 Banca Móvil\nApp Events]
        S2[🏧 ATMs\nIoT Events]
        S3[💻 Banca Web\nTransacciones]
        S4[🏦 Core Bancario\nLegacy APIs]
        S5[📊 Mercados\nFinancieros]
        S6[📅 Eventos\nCalendario]
    end

    subgraph INGESTION["⚡ CAPA DE INGESTA"]
        PS[Cloud Pub/Sub\nStreaming Queue]
        GCS_RAW[Cloud Storage\ngs://lumina-raw/\nData Lake - Zona Raw]
    end

    subgraph PROCESSING["⚙️ CAPA DE PROCESAMIENTO"]
        DF_STREAM[Cloud Dataflow\nStreaming Pipeline\nApache Beam]
        DF_BATCH[Cloud Dataflow\nBatch Pipeline\nApache Beam]
        DATAPROC[Cloud Dataproc\nPySpark Jobs\nHadoop Ecosystem]
    end

    subgraph STORAGE["🗄️ CAPA DE ALMACENAMIENTO"]
        GCS_PROC[Cloud Storage\ngs://lumina-processed/\nParquet / ORC]
        BQ_RAW[BigQuery\nlumina_raw]
        BQ_CUR[BigQuery\nlumina_curated]
        BQ_RPT[BigQuery\nlumina_reporting]
    end

    subgraph SERVING["📊 CAPA DE SERVICIO"]
        LOOKER[Looker Studio\nDashboards Operativos]
        API[Cloud Run\nREST APIs]
        ML[Vertex AI\nModelos ML]
    end

    subgraph GOV["🔐 GOBERNANZA & SEGURIDAD"]
        DATAPLEX[Dataplex\nGovernance & Lineage]
        CMPOSER[Cloud Composer\nOrchestration / Airflow]
        IAM[Cloud IAM\n+ VPC Service Controls]
    end

    S1 & S2 & S3 --> PS
    S4 --> GCS_RAW
    S5 & S6 --> GCS_RAW

    PS --> DF_STREAM
    GCS_RAW --> DF_BATCH
    GCS_RAW --> DATAPROC

    DF_STREAM --> BQ_RAW
    DF_BATCH --> BQ_RAW
    DF_BATCH --> GCS_PROC
    DATAPROC --> GCS_PROC
    DATAPROC --> BQ_CUR

    BQ_RAW --> BQ_CUR
    GCS_PROC --> BQ_CUR
    BQ_CUR --> BQ_RPT

    BQ_RPT --> LOOKER
    BQ_RPT --> API
    BQ_CUR --> ML

    DATAPLEX -.->|governa| STORAGE
    CMPOSER -.->|orquesta| PROCESSING
    IAM -.->|controla| INGESTION & PROCESSING & STORAGE
```

---

## 4. Arquitectura de Datos Detallada

### 4.1 Flujo de Ingesta (Hot Path – Streaming)

```mermaid
sequenceDiagram
    participant APP as 📱 App / ATM / Web
    participant PS as Cloud Pub/Sub<br/>lumina-transactions-stream
    participant DF as Cloud Dataflow<br/>Streaming Pipeline
    participant BQ_RAW as BigQuery<br/>lumina_raw.transactions_stream
    participant BQ_FRD as BigQuery<br/>lumina_raw.fraud_alerts
    participant NOTIFY as Cloud Run<br/>Notification Service

    APP->>PS: Publica evento de transacción (JSON)
    Note over PS: Buffer distribuido<br/>retención 7 días
    PS->>DF: Consume mensaje (push subscription)
    DF->>DF: 1. Parsear & validar schema
    DF->>DF: 2. Enriquecer con perfil de riesgo del cliente
    DF->>DF: 3. Aplicar reglas de detección de fraude
    DF->>DF: 4. Ventana temporal (60 seg tumbling)
    DF->>DF: 5. Agregar métricas de ventana

    alt Transacción Normal
        DF->>BQ_RAW: Inserir fila en tabla de streaming
    else Transacción Sospechosa
        DF->>BQ_RAW: Insertar con flag is_fraud_suspect=TRUE
        DF->>BQ_FRD: Registro en tabla de alertas
        BQ_FRD->>NOTIFY: Trigger → Notificación en tiempo real
    end
```

### 4.2 Flujo de Ingesta (Cold Path – Batch)

```mermaid
flowchart LR
    subgraph SOURCES_BATCH["Fuentes Batch"]
        LEGACY[Core Bancario\nExport Nightly\nCSV/JSON]
        MARKET[APIs Mercados\nFinancieros\nREST]
        ATM_LOG[Logs ATM\nSFTP Diario]
    end

    subgraph GCS_ZONES["Data Lake - Cloud Storage"]
        RAW[gs://lumina-raw/\nZona Raw\nFormato original]
        STAGE[gs://lumina-processed/\nZona Procesada\nParquet comprimido]
    end

    subgraph PROC["Procesamiento Batch"]
        DF_B[Dataflow Batch\nApache Beam\nETL + Calidad]
        SPARK[Dataproc Spark\nPySpark\nAnálisis Distribuido]
    end

    subgraph BQ["BigQuery"]
        RAW_BQ[lumina_raw\nTablas de staging]
        CURATED[lumina_curated\nDatos limpios y enriquecidos]
        REPORTING[lumina_reporting\nAggregations para BI]
    end

    LEGACY & MARKET & ATM_LOG -->|"Cloud Storage Transfer\n/ custom scripts"| RAW
    RAW -->|"Dataflow Lee"| DF_B
    DF_B -->|"Limpieza + Validación"| RAW_BQ
    DF_B -->|"Parquet Comprimido"| STAGE
    STAGE -->|"Spark Lee"| SPARK
    SPARK -->|"Risk Profiles\n+ Aggregations"| CURATED
    RAW_BQ -->|"SQL Views\nDataform"| CURATED
    CURATED -->|"SQL Aggregations"| REPORTING
```

### 4.3 Modelo de Datos Conceptual

```mermaid
erDiagram
    CLIENT {
        string client_id PK
        string full_name
        int age
        string district
        string risk_tier
        float credit_score
        string digital_preference
        string account_type
        timestamp created_at
    }

    ACCOUNT {
        string account_id PK
        string client_id FK
        string bank_origin
        string account_type
        float balance
        string currency
        string status
        timestamp last_activity
    }

    TRANSACTION {
        string transaction_id PK
        string account_id FK
        string client_id FK
        timestamp event_timestamp
        float amount
        string currency
        string channel
        string merchant_category
        string merchant_id
        float lat
        float lon
        string district
        boolean is_fraud_suspect
        float fraud_score
        string status
    }

    ATM_EVENT {
        string event_id PK
        string atm_id FK
        string client_id FK
        timestamp event_timestamp
        string event_type
        float amount
        string district
    }

    ATM {
        string atm_id PK
        string district
        float lat
        float lon
        int capacity_daily
        string status
    }

    FRAUD_ALERT {
        string alert_id PK
        string transaction_id FK
        string client_id FK
        timestamp alert_timestamp
        float fraud_score
        string rule_triggered
        string status
    }

    MARKET_DATA {
        date reference_date PK
        float interbank_rate
        float fx_usd
        float inflation_index
        boolean is_holiday
        string event_type
    }

    CLIENT ||--o{ ACCOUNT : "tiene"
    ACCOUNT ||--o{ TRANSACTION : "genera"
    CLIENT ||--o{ TRANSACTION : "realiza"
    CLIENT ||--o{ ATM_EVENT : "usa"
    ATM ||--o{ ATM_EVENT : "registra"
    TRANSACTION ||--o| FRAUD_ALERT : "puede generar"
```

---

## 5. Tecnologías GCP y Justificación

### 5.1 Stack Tecnológico Completo

| Capa | Servicio GCP | Open Source Base | Justificación |
|---|---|---|---|
| **Ingesta Streaming** | Cloud Pub/Sub | – | Cola de mensajes gestionada; desacoplamiento productor/consumidor; escalado automático; retención configurable (hasta 7 días) |
| **Procesamiento Streaming** | Cloud Dataflow | Apache Beam | Modelo unificado batch+stream; serverless (sin gestión de cluster); auto-scaling; exactamente-una-vez garantizado |
| **Procesamiento Batch** | Cloud Dataproc | Apache Spark / Hadoop | Cluster Spark/Hadoop gestionado; ideal para joins masivos sobre históricos; costo-efectivo con preemptible VMs |
| **Data Lake (Raw)** | Cloud Storage (GCS) | – | Almacenamiento de objetos exabyte-scale; bajo costo; soporte nativo de Parquet/ORC; integración directa con Dataflow y Dataproc |
| **Data Warehouse** | BigQuery | – | Motor analítico columnar serverless; consultas SQL sobre petabytes; integración con Looker, Vertex AI y Dataform |
| **Transformación SQL** | Dataform | dbt-like | Versionamiento de transformaciones SQL; linaje de datos; CI/CD para queries analíticas (DataOps) |
| **Orquestación** | Cloud Composer | Apache Airflow | DAGs para pipelines complejos; dependencias entre tareas; reintentos automáticos; visibilidad del flujo |
| **Gobernanza** | Dataplex | – | Linaje de datos automático; catalogación; gestión de políticas de acceso; calidad de datos |
| **ML / IA** | Vertex AI | TensorFlow/PyTorch | Entrenamiento y despliegue de modelos de detección de fraude; Feature Store para reutilización de features |
| **Seguridad** | Cloud IAM + VPC SC | – | Control de acceso granular por rol; Service Controls para aislar datos sensibles; sin exfiltración de datos |
| **Monitoreo** | Cloud Monitoring + Logging | – | Alertas de latencia de pipeline; dashboards de salud de infraestructura |
| **APIs / Microservicios** | Cloud Run | Docker | Microservicios serverless para exponer datos procesados al frontend |

### 5.2 Por Qué NO Kubernetes propio / On-Premise

- **Complejidad operativa**: DataLandia está migrando 12 sistemas legacy → prioridad en time-to-market
- **Elasticidad**: Picos de pago requieren escalado en minutos, no horas
- **Seguridad**: GCP provee compliance bancario (PCI-DSS, SOC 2) sin esfuerzo adicional
- **Costo**: Modelo de pago por uso en Dataflow/BigQuery >> mantener cluster 24/7

---

## 6. Seguridad y Gobernanza

```mermaid
flowchart TD
    subgraph SEC["🔐 Capas de Seguridad"]
        IAM["Cloud IAM\nRoles granulares por equipo:\n• data-engineers\n• data-analysts\n• risk-team\n• fraud-ops"]
        VPC["VPC Service Controls\nPerímetro de seguridad:\nBigQuery + GCS + Pub/Sub\nsin acceso desde internet"]
        CMEK["CMEK\nCustomer-Managed Encryption Keys\nCloud KMS para datos PII"]
        DLP["Cloud DLP\nDetección y enmascaramiento\nautomático de PII\n(DNI, tarjetas, cuentas)"]
    end

    subgraph GOV["📋 Gobernanza de Datos"]
        DATAPLEX["Dataplex\nCatálogo de datos\nLinaje automático\nPolíticas de calidad"]
        DATAFORM["Dataform\nVersionado de transformaciones SQL\nCI/CD de pipelines analíticos\nDocumentación de modelos"]
        AUDIT["Cloud Audit Logs\nRegistro inmutable de todos\nlos accesos a datos"]
    end

    subgraph CLASSIFY["🏷️ Clasificación de Datos"]
        PII["PII Sensible\nDNI, nombre, dirección\n→ Enmascarado + acceso restringido"]
        FINANCIAL["Financiero Confidencial\nSaldos, movimientos\n→ Cifrado CMEK + rol específico"]
        OPERATIONAL["Operativo Interno\nMétricas, logs de sistema\n→ Acceso estándar por equipo"]
        PUBLIC["Referencia Pública\nMercados, calendarios\n→ Sin restricción"]
    end

    IAM --> DATAPLEX
    VPC --> IAM
    CMEK --> PII & FINANCIAL
    DLP --> PII
    DATAPLEX --> AUDIT
    DATAFORM --> DATAPLEX
```

---

## 7. Pipeline de Detección de Fraude (Detalle)

```mermaid
flowchart LR
    subgraph INPUT["Entrada"]
        TX[Transacción Nueva\nJSON vía Pub/Sub]
    end

    subgraph ENRICH["Enriquecimiento"]
        PROFILE[Perfil de Cliente\nRisk Score + Historial\ndesde BigQuery read]
        GEO[Geolocalización\nVerificar ubicación\nvs. última transacción]
    end

    subgraph RULES["Motor de Reglas"]
        R1{Monto > 3x\npromedio histórico?}
        R2{Ubicación\nImposible en tiempo?}
        R3{> 5 transacciones\nen 60 seg?}
        R4{País de alto\nriesgo?}
    end

    subgraph SCORE["Scoring"]
        FRAUD_SCORE[Calcular Fraud Score\n0.0 - 1.0\nSuma ponderada de reglas]
    end

    subgraph ACTION["Acción"]
        APPROVE[✅ Aprobar\nscore < 0.3]
        REVIEW[⚠️ Revisión\n0.3 ≤ score < 0.7]
        BLOCK[🚫 Bloquear\nscore ≥ 0.7]
    end

    TX --> PROFILE
    TX --> GEO
    PROFILE & GEO --> R1 & R2 & R3 & R4
    R1 & R2 & R3 & R4 --> FRAUD_SCORE
    FRAUD_SCORE --> APPROVE & REVIEW & BLOCK
```

---

## 8. Planificación de Liquidez (Vista General)

```mermaid
flowchart TB
    subgraph INPUTS["Entradas Diarias (Batch)"]
        HIST[Histórico de\nRetiros por ATM]
        MARKET[Tasas Interbancarias\ny Tipo de Cambio]
        CAL[Calendario de Eventos\nFestivos, Ferias, Quincenas]
        TREND[Tendencias de\nMovilidad y Gasto]
    end

    subgraph PROC["Procesamiento Dataproc / Spark"]
        FEAT[Feature Engineering\nSpark MLlib]
        MODEL[Modelo Predictivo\nRegresión / Gradient Boosting]
        PREDICT[Predicción de Demanda\npor ATM / Distrito]
    end

    subgraph OUTPUT["Salidas"]
        PLAN[Plan Diario de Liquidez\nBigQuery lumina_reporting.liquidity_plan]
        ALERT[Alertas de ATMs\ncon riesgo de quedarse sin efectivo]
        DASHBOARD[Dashboard Operativo\nLooker Studio]
    end

    HIST & MARKET & CAL & TREND --> FEAT
    FEAT --> MODEL
    MODEL --> PREDICT
    PREDICT --> PLAN
    PREDICT --> ALERT
    PLAN & ALERT --> DASHBOARD
```

---

## 9. Estrategia de Migración desde 12 Bancos

```mermaid
timeline
    title Roadmap de Migración a Lumina Bank
    section Fase 0 - Fundamentos (Meses 1-2)
        Infraestructura GCP: Buckets GCS, BigQuery datasets, VPC, IAM
        Esquema Unificado: Modelo de datos canónico (cliente, cuenta, transacción)
    section Fase 1 - Ingesta (Meses 3-4)
        Pipelines de Migración: Dataflow batch para históricos de 12 bancos
        Pub/Sub Setup: Integración de canales digitales en tiempo real
    section Fase 2 - Procesamiento (Meses 5-6)
        Pipelines Activos: Streaming fraud detection + Batch reporting
        Data Lake Completo: Todos los datos históricos consolidados en GCS
    section Fase 3 - Analítica (Meses 7-9)
        Vertex AI: Modelos de riesgo y fraude entrenados con datos unificados
        Looker Dashboards: Reportes operativos y de liquidez
    section Fase 4 - Optimización (Meses 10-12)
        Agentes IA: Agent Engine SDK para asesoría financiera personal
        Orquestación: Cloud Composer para automatización end-to-end
```

---

## 10. Dimensionamiento Estimado

| Métrica | Estimado | Fuente |
|---|---|---|
| Clientes activos | 9,000,000 | Caso de estudio |
| Transacciones/día (normal) | ~5,000,000 | ~0.5-1 tx/cliente/día |
| Transacciones/día (pico pago) | ~25,000,000 | 5x factor pico |
| Eventos Pub/Sub/seg (pico) | ~300 msg/s | 25M / 86400s |
| Volumen raw diario | ~50-100 GB | ~2KB/evento promedio |
| Volumen histórico (12 bancos, 5 años) | ~180 TB | 100 GB/día × 5 años |
| Tamaño BigQuery estimado (primer año) | ~36 TB | sin compresión |
| Latencia objetivo (fraude) | < 2 segundos | SLA de autorización |
| Latencia objetivo (batch KPIs) | < 2 horas | SLA operativo |

---

## 11. Entregables del Proyecto

| Entregable | Descripción | Archivos |
|---|---|---|
| **E1 (Evaluación)** | Diseño de arquitectura + justificación tecnológica | `architecture.md` |
| **P1 (Pipeline)** | Implementación de ingesta y procesamiento distribuido | `pipelines/`, `data_generation/`, `infra/` |
| **P2 (ML)** | Modelos Vertex AI + RAG | *(futuro)* |
| **P3 (Agente)** | Agente inteligente con Cloud Composer + Cloud Run | *(futuro)* |

---

## 12. Referencias

- [Google Cloud Architecture Center – Financial Services](https://cloud.google.com/architecture/financial-services)
- [Apache Beam Programming Guide](https://beam.apache.org/documentation/programming-guide/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Ted Malaska & Jonathan Seidman (2018). Foundations for Architecting Data Solutions. O'Reilly.]
- [Google Cloud Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Cloud Dataproc – Spark/Hadoop](https://cloud.google.com/dataproc/docs)
