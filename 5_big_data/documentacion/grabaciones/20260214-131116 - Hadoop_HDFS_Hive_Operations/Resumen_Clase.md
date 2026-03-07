# Resumen de Clase: Operaciones con Hadoop, HDFS y Hive

**Fecha:** 14 de Febrero de 2026  
**Contexto:** Clase de Maestría en Big Data - Modernización de Infraestructura y Arquitecturas de Datos.

## Resumen Ejecutivo

La sesión se centró en la arquitectura fundamental de Big Data utilizando el ecosistema Hadoop desplegado en Google Cloud Platform (GCP). Se cubrieron desde conceptos teóricos de arquitectura y FinOps hasta la ejecución práctica de comandos en HDFS y Hive. El objetivo principal fue entender cómo manipular datos en un entorno distribuido, la importancia de desacoplar el cómputo del almacenamiento y las mejores prácticas para la gestión de tablas en Hive.

---

## Temas Discutidos

### 1. Infraestructura Cloud y Google Cloud Platform (GCP)
*   **DataProc:** Servicio gestionado de GCP para correr clusters de Hadoop/Spark. Se explicó la configuración de nodos:
    *   *Nodo Maestro (Master):* Contiene el NameNode y YARN ResourceManager.
    *   *Nodos Trabajadores (Workers):* Contienen los DataNodes. Mínimo 2 para redundancia.
    *   *Nodos Secundarios:* Útiles para procesamiento adicional (computación pura) sin almacenamiento HDFS. Se sugirió usar instancias *Preemptible* (más baratas) para estos nodos.
*   **Gestión de Proyectos e IAM:** Importancia de asignar roles granulares (ej. DataProc Admin) en lugar de roles amplios como "Editor".
*   **FinOps (Optimización de Costos):**
    *   Estrategias para reducir el gasto en la nube.
    *   **Committed Use Discounts (CUDs):** Contratos de 1 a 3 años para obtener descuentos significativos en máquinas virtuales si la carga de trabajo es predecible.
    *   Monitoreo de cuotas de región y CPU.
*   **Arquitectura de Migración:**
    *   *Lift & Shift:* Mover máquinas virtuales on-premise a la nube tal cual (IaaS).
    *   *Refactorización:* Mover hacia Kubernetes (GKE) o servicios PaaS para mayor eficiencia.
    *   *Networking:* Uso de VPCs privadas y Cloud NAT para seguridad, evitando exponer los clusters directamente a internet.

### 2. Ecosistema Hadoop
*   **HDFS (Hadoop Distributed File System):** Sistema de archivos distribuido. Es la capa de almacenamiento.
*   **YARN:** Orquestador de recursos del cluster.
*   **MapReduce vs. Spark:** MapReduce escribe en disco (lento), mientras que Spark procesa en memoria (rápido). Spark es el estándar actual.
*   **Hive:** Data Warehouse sobre Hadoop. Permite consultas SQL (HQL). Convierte SQL en trabajos MapReduce (o Tez/Spark).
*   **Formatos de Archivo:**
    *   **Parquet:** Columbar, ideal para lecturas rápidas y analítica (Estándar en Big Data).
    *   **Avro:** Basado en filas, bueno para escritura.
    *   **CSV/TextFile:** Común para ingesta cruda pero menos eficiente.

### 3. Arquitectura de Datos y Mejores Prácticas
*   **Desacoplamiento:** **No guardar datos persistentes en el HDFS del cluster**, ya que si el cluster se borra, la data se pierde. La buena práctica es usar almacenamiento de objetos (Google Cloud Storage, AWS S3) como la capa persistente ("Data Lake").
*   **Tablas en Hive:**
    *   **Tablas Nativas (Managed):** `DROP TABLE` borra tanto la metadata como los datos en HDFS.
    *   **Tablas Externas (External):** `DROP TABLE` solo borra la metadata. Los datos quedan intactos en HDFS/Storage. **Esta es la práctica recomendada** para evitar pérdida accidental de datos históricos.
*   **Particionamiento:** Organizar los datos en carpetas jerárquicas (Año/Mes/Día) para optimizar el rendimiento de las consultas, evitando escanear todo el dataset.

---

## 🧪 Laboratorio Realizado

Sí, se realizaron laboratorios prácticos divididos en dos partes principales. Los estudiantes trabajaron conectados vía SSH al nodo maestro de su cluster DataProc.

### Parte 1: HDFS y Scripting en Linux
**Objetivo:** Familiarizarse con la consola, gestión de archivos y automatización.

1.  **Conexión:** Acceso mediante SSH al cluster.
2.  **Comandos Ejecutados:**
    *   Gestión local (Linux): `ls`, `mkdir`, `touch` (crear archivos vacíos), `nano`/`vi` (edición).
    *   Gestión HDFS:
        *   `hdfs dfs -ls /`: Listar archivos en el sistema distribuido.
        *   `hdfs dfs -mkdir -p /user/alumno/carpeta`: Crear directorios recursivos.
        *   `hdfs dfs -put archivo_local.txt /ruta_hdfs/`: Subir archivos de Linux a HDFS.
        *   `hdfs dfs -cat archivo`: Leer contenido.
        *   `hdfs dfs -rm -r carpeta`: Eliminar carpetas.
3.  **Automatización (Shell Script):**
    *   Se subió y ejecutó un script `.sh` (`laboratorio.sh`).
    *   El script automatizaba la limpieza de carpetas previas, creación de estructuras de directorios y carga de datasets (`persona.data`, `transacciones.data`, `titanic.csv`).
    *   Uso de variables en Bash (`$1`) para parametrizar el nombre del usuario y reutilizar el código.
4.  **Permisos:** Se explicó el sistema octal (777, 750) para control de acceso (Lectura/Escritura/Ejecución) para Usuario/Grupo/Otros.

### Parte 2: Hive y Gestión de Tablas
**Objetivo:** Estructurar los datos cargados en HDFS mediante esquemas SQL.

1.  **Setup:** Se abrieron dos terminales SSH en paralelo (una para comandos HDFS/Linux y otra para la consola de `hive`).
2.  **Creación de Base de Datos:**
    *   Uso de `CREATE DATABASE IF NOT EXISTS nombre_db LOCATION '/ruta/hdfs';`. Se definió una ruta específica en HDFS para almacenar los datos de la DB.
3.  **Tablas Externas:**
    *   Se creó una tabla externa para `transacciones`.
    *   Comando clave: `CREATE EXTERNAL TABLE ... ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' ... LOCATION ...`.
4.  **Ingesta de Datos:**
    *   Uso de `LOAD DATA LOCAL INPATH 'archivo_linux' INTO TABLE tabla PARTITION (...)`.
    *   Se demostró cómo cargar datos desde el sistema de archivos local de Linux directamente a una partición específica de Hive.
5.  **Validación:**
    *   `SHOW DATABASES;`, `SHOW TABLES;`.
    *   `SELECT * FROM transacciones LIMIT 10;`.
    *   `SELECT COUNT(*) ...` (esto dispara un trabajo MapReduce internamente).
    *   Se verificó que al borrar la tabla (`DROP TABLE`), los archivos físicos permanecían en HDFS, confirmando la teoría de tablas externas.

### Tarea Asignada
*   Los alumnos deben replicar los ejercicios:
    1.  Ejecutar el script de HDFS optimizado con su nombre de usuario.
    2.  Crear la estructura en Hive, cargar las particiones restantes de los archivos de transacciones.
    3.  Enviar capturas de pantalla de ambas ejecuciones.
