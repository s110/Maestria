# Resumen de la Clase: Arquitecturas Modernas de Datos

**Fecha:** 30 de Enero de 2026 (según nombre del archivo)
**Instructora:** Anita Quevedo

## 1. Introducción y Objetivos
La clase se centró en definir y explorar las arquitecturas modernas de datos, con el objetivo de desarrollar terminología clave, entender conceptos fundamentales como la arquitectura "Medallion", y diferenciar entre formatos de datos como Parquet, Avro, Delta Lake, Apache Iceberg y Hudi. También se discutieron buenas prácticas y componentes de una arquitectura de datos.

## 2. Evolución de las Arquitecturas de Datos

### Primera Generación: Data Warehouse
*   **Enfoque:** Datos estructurados centralizados.
*   **Componentes:** Data Marts (ventas, compras, logística) que alimentan el Data Warehouse.
*   **Proceso:** ETL (Extract, Transform, Load).
*   **Desventajas:** Rigidez (cambios en el esquema son costosos), infraestructura fija y costosa.

### Segunda Generación: Data Lake
*   **Enfoque:** Almacenamiento de datos estructurados, semi-estructurados y no estructurados (logs, redes sociales, audio, video).
*   **Tecnología:** HDFS (Hadoop File System) o almacenamiento en la nube (Amazon S3, Azure Blob Storage, Google Cloud Storage).
*   **Proceso:** ELT (Extract, Load, Transform).
*   **Desventajas:** Puede convertirse en un "pantano de datos" si no hay gobernanza adecuada.

### Tercera Generación: Data Lakehouse
*   **Concepto:** Combina la flexibilidad del Data Lake con la gestión y calidad del Data Warehouse.
*   **Características:**
    *   Soporta formatos abiertos (Delta Lake, Apache Iceberg, Apache Hudi).
    *   Incorpora propiedades ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad).
    *   Permite gobernanza de datos y esquemas.
*   **Uso:** Ideal para empresas que buscan calidad, gobernanza y escalabilidad.

### Data Mesh
*   **Concepto:** Arquitectura descentralizada orientada al dominio.
*   **Características:**
    *   Los datos se tratan como productos.
    *   Propiedad descentralizada (cada área como Ventas o Logística es dueña de sus datos).
    *   Gobernanza federada.
*   **Uso:** Recomendado para compañías grandes y complejas con múltiples unidades de negocio.

## 3. Conceptos Clave y Buenas Prácticas

### Arquitectura Medallion (Capas de Datos)
Se recomienda estructurar los datos en tres capas principales:
1.  **Capa Bronce (Raw):** "La verdad pura". Datos crudos tal cual llegan de la fuente. Se sugiere guardar todo como `String` para evitar pérdidas de precisión o errores de formato iniciales.
2.  **Capa Plata (Silver):** Datos limpios y transformados. Se definen tipos de datos correctos, se eliminan duplicados y se aplican reglas de negocio y calidad.
3.  **Capa Oro (Gold):** Datos agregados y listos para el análisis y consumo (reportes, dashboards).

### Formatos de Tabla Abiertos (Open Table Formats)
Se discutieron las ventajas de utilizar formatos que permiten transacciones ACID y "viajes en el tiempo" (Time Travel) sobre Data Lakes:
*   **Delta Lake:** Permite actualizaciones (upserts) y versionamiento.
*   **Apache Iceberg:** Desarrollado por Netflix. Enfocado en alta concurrencia, confiabilidad y manejo eficiente de grandes volúmenes de datos históricos (viajes en el tiempo).
*   **Apache Hudi:** Optimizado para streaming y CDC (Change Data Capture) en tiempo real.

### Otras Consideraciones
*   **Seguridad:** Principio de "Zero Trust", enmascaramiento de datos sensibles (PII), y gestión de accesos (IAM/RBAC).
*   **Costos y Rendimiento:** Importancia de elegir el tipo de dato correcto (e.g., `Parquet` para lectura rápida en modelos, `Avro` para escritura).
*   **Contratos de Datos (Data Contracts):** Definir expectativas (SLA, SLO, esquemas) entre productores y consumidores de datos antes de implementar.

## 4. Proyectos del Curso (Talleres)
La instructora explicó los proyectos que los alumnos desarrollarán en grupos (de 3 a 5 personas):
*   **Temas:** Banca, Retail, Transporte (Smart Mobility).
*   **Requisitos:** Implementar una arquitectura que soporte Batch y Streaming, definir modelos de datos, gobierno, seguridad y justificación de costos.
*   **Entregable Final:** Implementación técnica y sustentación de la arquitectura.

## 5. MLOps y Despliegue de Modelos
Hacia el final, se tocó brevemente cómo desplegar modelos de Machine Learning:
*   Uso de `Pickle` para serializar modelos.
*   Creación de APIs (usando Fast API o similar) para exponer los modelos.
*   La instructora acordó ajustar el sílabo para incluir más contenido sobre **MLOps**, respondiendo a la solicitud de un alumno.

---

## Sobre el Laboratorio
**Nota:** En esta grabación **NO se realizó el laboratorio práctico** paso a paso.
Aunque estaba planificado, la instructora indicó explícitamente: *"puesto que la parte del laboratorio lo vamos a dejar un poquito para poder explicarles los talleres Primero"*. La sesión se dedicó a la teoría, la explicación de los proyectos finales y la resolución de dudas, posponiendo la parte práctica para una futura sesión o para que los alumnos revisen el material asíncronamente.
