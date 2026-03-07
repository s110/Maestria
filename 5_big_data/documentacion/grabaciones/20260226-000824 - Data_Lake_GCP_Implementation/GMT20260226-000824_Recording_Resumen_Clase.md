# Resumen de Clase: Data Lake GCP Implementation
**Fecha del registro:** 26 de febrero de 2026  
**Instructora:** Anita Quevedo

## 1. Resumen Ejecutivo
La sesión se centró en la implementación práctica de un Data Lake en Google Cloud Platform (GCP). Se realizó un repaso de conceptos clave de Hadoop (HDFS, Hive, formatos de archivo), se ejecutó un laboratorio completo de ingesta y procesamiento de datos utilizando Dataproc y scripts de automatización (Shell/HiveQL), y se introdujo una nueva arquitectura *serverless* para un caso de uso "End-to-End" que involucra digitalización de documentos y geolocalización, el cual será el foco de la próxima sesión y del examen.

## 2. Anuncios Importantes
*   **Modalidad de Clases:** Debido a un tema de salud (rehabilitación física de la instructora), las sesiones con ella (incluyendo la de este sábado a partir de las 3:30 PM) serán **virtuales**. La sustentación final sí será presencial.
*   **Participación ("Dedocracia"):** Se cambiará la dinámica de participación voluntaria a llamar lista específicamente a quienes no han participado para asegurar notas completas para todos.
*   **Examen / Trabajo Final:**
    *   Consistirá en un caso de uso "End-to-End" (similar al que se explicará en clase) donde deberán plantear una arquitectura, resolver el problema de negocio y realizar estimación de costos.
    *   Se permite trabajar en grupos (de 3 a 5 personas).
    *   Los alumnos deben ir pensando en su propio caso de uso de negocio.

## 3. Repaso de Arquitectura Hadoop
Se validaron conocimientos previos mediante preguntas a la clase:
*   **HDFS:** Sistema de archivos distribuido para almacenamiento.
*   **Hive:** Data Warehouse sobre Hadoop para consultas SQL-like. Se discutió la diferencia entre tablas **Internas** (Managed) y **Externas** (al borrar la tabla externa, los datos en HDFS persisten; en la interna se borran).
*   **Particionamiento:** Estrategia clave para optimizar costos y tiempos de consulta (e.g., particionar por Año/Mes/Día). Se mencionó que herramientas como BigQuery y EMR sugieren particionar por fecha (Date/Integer), aunque Hadoop permite particionar por strings (ej. unidad organizativa).
*   **Formatos de Archivo:**
    *   **Avro:** Bueno para escritura rápida (Row-oriented). Requiere gestión de esquemas (`.avsc`).
    *   **Parquet:** Estándar de facto para analítica (Column-oriented), altamente eficiente para lectura y compresión.
    *   **Snappy:** Formato de compresión recomendado (balance entre velocidad y tasa de compresión), similar conceptualmente a un ZIP pero splittable.

## 4. Laboratorio 1: Data Lake con Dataproc y Hive
Este laboratorio se realizó durante la clase para implementar las capas del Data Lake (Landing, Universal, Smart).

### A. Configuración del Entorno
1.  **Validación de Créditos:** Se verificó que los alumnos tuvieran créditos activos en GCP.
2.  **Creación del Cluster Dataproc:**
    *   Se utilizó **Cloud Shell** en lugar de la consola visual para agilizar el proceso.
    *   Comando utilizado: `gcloud dataproc clusters create ...` (reemplazando `PROJECT_ID` y nombre del cluster).
3.  **Permisos IAM (Service Account):**
    *   Al crear el cluster por primera vez, es necesario asignar roles a la *Service Account* por defecto:
        *   `Dataproc Worker`
        *   `Storage Admin`
        *   `Storage Object Admin`

### B. Ejecución del Flujo de Datos
1.  **Carga de Archivos:**
    *   Se subieron al Cloud Shell 9 archivos: `persona.data`, `empresa.data`, `transacciones.data` (y sus variantes), esquemas Avro (`.avsc`) y scripts (`.sh`, `.sql`).
    *   **Importante:** Se instruyó modificar los scripts `.sh` para reemplazar el placeholder "Anita Quevedo" con el nombre del alumno antes de ejecutar.
2.  **Automatización con Shell Scripts:**
    *   Se explicó el uso de scripts `.sh` para orquestar comandos HDFS (`hadoop fs -put`) y Hive (`hive -f file.sql`).
    *   **Script Maestro:** Se ejecutó el script `19_execute_all.sh` (o similar), el cual llama secuencialmente a los scripts numerados (14 al 18) para desplegar todo el pipeline.
3.  **Arquitectura Desplegada:**
    *   **Capa Landing/TMP:** Ingesta de archivos planos (TextFile/CSV) hacia HDFS y tablas Hive externas.
    *   **Transformación:** Conversión de formatos (Text -> Avro -> Parquet).
    *   **Capa Universal:** Tablas particionadas (ej. `transacciones` particionada por fecha) y almacenadas como **Parquet** con compresión **Snappy**.
    *   **Manejo de Esquemas:** Uso de esquemas Avro externos para definir la estructura de los datos.

### C. Cierre del Laboratorio
*   **Limpieza:** Se ordenó **ELIMINAR el cluster de Dataproc** al finalizar la clase para evitar cobros innecesarios, ya que no se usará en la siguiente sesión.

## 5. Introducción al Caso de Uso "End-to-End" (Laboratorio 2)
Se presentó el caso de negocio que se desarrollará a fondo el sábado.

*   **Problemática:** Empresa con miles de documentos físicos (facturas/guías), digitación manual propensa a errores, lentitud y falta de visibilidad de entregas.
*   **Requerimiento:** Arquitectura *Serverless* y *Costo-eficiente*.
*   **Arquitectura Propuesta:**
    1.  **Ingesta:** Archivos subidos a Cloud Storage.
    2.  **Procesamiento (OCR):** Cloud Functions activa **Document AI API** para extraer datos.
    3.  **Almacenamiento:** Metadata JSON a GCS y datos estructurados a **BigQuery**.
    4.  **Enriquecimiento Geoespacial (Real-time):**
        *   Eventos capturados vía **Pub/Sub**.
        *   Cloud Function llama a **Geocoding API** (Google Maps) para obtener latitud/longitud de las direcciones.
        *   Almacenamiento de datos geoespaciales en BigQuery (tipo `GEOGRAPHY`).
    5.  **Visualización:** Mapas en Looker Studio/PowerBI.

### Avance realizado en clase:
1.  **Habilitación de APIs:** Se ejecutaron comandos para habilitar `Document AI API`, `Geocoding API`, etc.
2.  **Creación de Credenciales:**
    *   Se creó una **API Key** en "APIs & Services".
    *   **Seguridad:** Se editó la API Key para añadir **restricciones**, limitando su uso únicamente a la **Geocoding API**.
    *   Se mencionó *Secret Manager* como buena práctica para guardar estas llaves (aunque no se implementó en este paso).

## 6. Próximos Pasos (Sábado)
*   Continuar con la implementación de la arquitectura Serverless (Cloud Functions, integración con APIs).
*   Trabajo en grupos para avanzar el laboratorio.
