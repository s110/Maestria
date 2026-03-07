# Resumen de Clase: Serverless Document Processing
**Fecha:** 28 de Febrero de 2026

## Resumen de la Clase

En esta sesión se abordó la implementación de una **arquitectura Serverless** para el procesamiento de documentos (facturas) de extremo a extremo (End-to-End). El objetivo principal fue resolver una problemática de negocio relacionada con la digitalización de documentos físicos, automatizando la extracción de información y su enriquecimiento con datos geoespaciales.

Se explicaron conceptos clave como:
*   **Serverless:** Uso de Cloud Functions (Gen 1 vs Gen 2) y Cloud Run, destacando las diferencias en tiempos de espera (timeouts) y casos de uso.
*   **Document AI:** Utilización de procesadores pre-entrenados (Form Parser) para extraer entidades de documentos PDF/imágenes sin necesidad de entrenar modelos desde cero.
*   **Arquitectura de Eventos:** Cómo los archivos subidos a Cloud Storage disparan funciones que orquestan el flujo de datos a través de Pub/Sub y BigQuery.

## Laboratorio: Procesamiento Serverless de Facturas

El laboratorio consistió en desplegar una tubería de datos (pipeline) automatizada en Google Cloud Platform (GCP).

### Arquitectura Implementada
1.  **Ingesta:** Archivo subido a Cloud Storage (Bucket Input).
2.  **Procesamiento Inicial:** Trigger de Cloud Function (`process-invoice`).
3.  **Extracción:** Llamada a la API de **Document AI** para extraer datos de la factura.
4.  **Orquestación:** Envío de datos extraídos a un tópico de **Pub/Sub**.
5.  **Enriquecimiento:** Trigger de Cloud Function (`geocode-address`) desde Pub/Sub.
6.  **Geocodificación:** Llamada a la **Google Maps Geocoding API** para obtener latitud/longitud de la dirección.
7.  **Almacenamiento:** Inserción de los datos enriquecidos en **BigQuery**.
8.  **Archivado:** Movimiento del archivo procesado a un Bucket Archive.

### Pasos Realizados

#### 1. Configuración del Entorno
*   Habilitación de APIs necesarias: Cloud Functions, Cloud Build, Document AI, Geocoding, Cloud Storage, Pub/Sub.
*   Clonación del repositorio de código y preparación del entorno en Cloud Shell.

#### 2. Creación de Recursos
*   **Cloud Storage:** Creación de tres buckets únicos (usando el Project ID):
    *   `input`: Para la recepción de facturas.
    *   `output`: Para salidas intermedias (JSONs).
    *   `archive`: Para almacenar facturas procesadas.
*   **Document AI:** Creación de un procesador de tipo **Form Parser** (General). Se guardó el `PROCESSOR_ID`.
*   **BigQuery:** Creación de un Dataset y una Tabla con esquema definido.
*   **Pub/Sub:** Creación de un tópico para la comunicación entre funciones.

#### 3. Configuración de Permisos (IAM)
Se identificó que el Service Account por defecto de App Engine (o el específico usado para las funciones) requería permisos explícitos para interactuar con los otros servicios. Se asignaron los siguientes roles:
*   `BigQuery Admin` y `BigQuery Job User`
*   `Document AI Administrator`
*   `Pub/Sub Admin`, `Pub/Sub Publisher` y `Pub/Sub Editor`
*   `Service Account Token Creator`
*   `Storage Admin`, `Storage Object Admin` y `Storage Object Creator`
*   `Cloud Run Admin` / `Cloud Build Service Account` (para el despliegue).

#### 4. Despliegue de Cloud Functions (Gen 1)

**Función 1: `process-invoice`**
*   **Trigger:** Evento de Cloud Storage (Finalize/Create en bucket `input`).
*   **Variables de Entorno configuradas:**
    *   `PROCESSOR_ID`: ID del procesador de Document AI.
    *   `PARSER_LOCATION`: Región del procesador (ej. `us`).
    *   `GOOGLE_CLOUD_PROJECT`: ID del proyecto.
    *   `OUTPUT_BUCKET`: Nombre del bucket de salida.
    *   `ARCHIVE_BUCKET`: Nombre del bucket de archivo.
    *   `TOPIC_ID`: ID del tópico de Pub/Sub.

**Función 2: `geocode-address`**
*   **Trigger:** Mensaje de Pub/Sub.
*   **Variables de Entorno configuradas:**
    *   `API_KEY`: Clave de API de Google Maps (obtenida de Credenciales).

#### 5. Pruebas y Validación
*   Limpieza de la tabla de BigQuery (`DELETE FROM ...`).
*   Subida de un archivo de factura al bucket `input`.
*   Verificación de logs en Cloud Functions para confirmar ejecución sin errores.
*   Validación de datos en BigQuery: Se confirmó la inserción de registros con datos de la factura y coordenadas geográficas.
*   Confirmación de que el archivo se movió automáticamente al bucket `archive`.

### Tarea / Desafío
*   Implementar un manejo de errores (alertas).
*   Crear un procesador especializado **Invoice Parser** en Document AI.
*   Generar un Dashboard (Looker Studio/Power BI) que muestre gastos por proveedor y un mapa de ubicaciones.
