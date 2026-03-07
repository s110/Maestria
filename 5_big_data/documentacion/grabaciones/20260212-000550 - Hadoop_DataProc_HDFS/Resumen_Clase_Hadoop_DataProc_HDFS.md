# Resumen de Clase: Hadoop, DataProc y HDFS

**Fecha de grabación:** 12 de Febrero de 2026 (Según nombre de archivo)
**Instructor:** Anita Quevedo

## 1. Objetivos de la Sesión
*   **Entender y configurar un clúster de Hadoop en la nube** utilizando Google Cloud Dataproc.
*   **Diseñar una arquitectura de datos elástica**, desacoplando el cómputo del almacenamiento.
*   **Optimización de costos y rendimiento**, incluyendo el uso de máquinas virtuales *Spot* (preemptible).
*   **Armar un pipeline de datos**, integrando ingesta, almacenamiento y procesamiento.

## 2. Contexto de Negocio y Problemática
Se discutió la necesidad de migrar de soluciones *on-premise* a la nube debido a:
*   **Escalabilidad:** Necesidad de soportar picos de tráfico (ej. Cyber Days).
*   **Costos de infraestructura:** Reducción de costos de mantenimiento y adopción del modelo de pago por uso.
*   **Silos de información:** Dificultad para integrar tecnologías como Spark, Hive y Machine Learning en sistemas rígidos.

## 3. Arquitectura y Tecnologías Discutidas

### Ecosistema Hadoop
Se explicó la arquitectura base de Hadoop y cómo ha evolucionado:
*   **HDFS (Hadoop Distributed File System):** Sistema de archivos distribuido. Base del almacenamiento.
*   **YARN:** Orquestador de recursos (CPU, RAM).
*   **MapReduce:** Modelo de procesamiento original (lento, basado en disco).
*   **Hive:** Almacén de datos (Data Warehouse) sobre Hadoop que permite usar SQL (HQL). Facilita la consulta de datos en HDFS.
*   **Spark:** Motor de procesamiento en memoria, mucho más rápido que MapReduce. Soporta Python (PySpark), Scala, Java, R y SQL.
*   **HBase:** Base de datos NoSQL de baja latencia.

### Componentes de la Arquitectura de Datos Moderno
*   **Ingesta:**
    *   *Batch:* Scoop (para RDBMS a Hadoop, aunque inseguro por manejo de credenciales), Data Fusion.
    *   *Streaming:* Apache Kafka (Open Source), Pub/Sub (Google Cloud), Kinesis (AWS).
*   **Almacenamiento (Data Lake):**
    *   Uso de **Cloud Storage** (buckets) como capa de almacenamiento desacoplada (similar a HDFS pero más barato y persistente).
    *   Formatos de tabla modernos: **Apache Iceberg, Hudi, Delta Lake**.
*   **Procesamiento:** Dataproc (Spark/Hadoop gestionado), Dataflow (Apache Beam serverless).
*   **Orquestación:** Cloud Composer (Apache Airflow gestionado).
*   **Gobierno y Seguridad:** Dataplex, IAM, VPCs, Cloud NAT.

## 4. Laboratorio: Creación y Gestión de Clúster en Dataproc

**Sí, se realizó un laboratorio práctico.** A continuación se detallan los pasos y actividades realizadas:

### Parte A: Configuración y Despliegue del Clúster
1.  **Habilitación de APIs:** Se activó la API de **Cloud Dataproc** en la consola de Google Cloud.
2.  **Creación del Clúster (Modo Standard/Single Node):**
    *   Se optó por un clúster de **Single Node** (1 maestro, 0 trabajadores) para propósitos de prueba y ahorro de costos, aunque se explicó que en producción se usa *Standard* (1 maestro, N trabajadores) o *High Availability* (3 maestros).
    *   **Configuración de Hardware:** Máquina tipo `n4-standard-2` (2 vCPU, 8GB RAM).
    *   **Red (Networking):** Se utilizó la red `default`. Se explicó el concepto de **VPC** (Red Privada Virtual), Subnets y reglas de Firewall para aislar y asegurar el clúster.
    *   **Component Gateway:** Se mencionó su activación para acceder a interfaces web (Jupyter, Hive, etc.).
3.  **Solución de Errores (Troubleshooting):**
    *   Un estudiante reportó un error de permisos durante la creación.
    *   **Solución:** Se accedió a IAM y se otorgaron los roles `Dataproc Worker`, `Dataproc Administrator` y `Storage Admin` a la cuenta de servicio (Service Account) utilizada por el clúster.

### Parte B: Interacción con HDFS y Comandos Linux
1.  **Conexión SSH:** Una vez el clúster estuvo activo (estado verde), se conectaron a la máquina virtual maestra vía SSH desde la consola.
2.  **Diferencia entre File Systems:** Se demostró la diferencia entre el sistema de archivos local de Linux (`ls`) y el sistema distribuido HDFS (`hdfs dfs -ls`).
3.  **Comandos Ejecutados:**
    *   `hdfs dfs -ls /`: Listar archivos en la raíz de HDFS.
    *   `hdfs dfs -mkdir /user/<nombre_usuario>`: Crear directorio de usuario en HDFS.
    *   `hdfs dfs -mkdir -p /ruta/recursiva`: Crear directorios anidados recursivamente.
    *   `hdfs dfs -put <archivo_local> <ruta_hdfs>`: Subir archivos del sistema local Linux a HDFS.
    *   `hdfs dfs -cat <archivo>`: Ver contenido de un archivo en HDFS.
    *   `hdfs dfs -rm -r <carpeta>`: Eliminar carpetas recursivamente.
    *   `hdfs dfs -chmod -R 777 <carpeta>`: Cambiar permisos de archivos/carpetas (Lectura, Escritura, Ejecución).
4.  **Carga de Datos:**
    *   Se subió el archivo `persona.data` (provisto en los recursos del curso) al entorno Linux mediante la opción "Upload file" de la consola.
    *   Se movió este archivo desde Linux hacia una carpeta creada en HDFS.

### Parte C: Automatización (Introducción)
*   Se mencionó el uso de scripts `.sh` (Shell scripts) para automatizar la secuencia de comandos HDFS y configuraciones, lo cual será profundizado en la siguiente clase.

## 5. Próximos Pasos (Clase del Sábado)
*   Profundizar en **Hive** y la creación del **Data Lake** a nivel de comandos.
*   Ejecución de scripts de automatización (`.sh`).
*   Introducción a modelos de Machine Learning sobre Big Data (Spark ML).
*   **Instrucción final:** Detener (*Stop*) el clúster para evitar consumos innecesarios de crédito hasta la próxima sesión.
