-- -------------------------------------------------------------------------------------------------------
-- 
-- @copyright Anita Quevedo
-- 
-- -------------------------------------------------------------------------------------------------------

-- COMANDO DE EJECUCION
-- beeline -u jdbc:hive2:// -f Laboratorio_017_deploy_database_universal.sql --hiveconf "PARAM_USERNAME=anitaquevedo"

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 1. Definición de parámetros
-- 
-- -------------------------------------------------------------------------------------------------------

-- [HIVE] Creamos una variable en HIVE
-- SET PARAM_USERNAME=anitaquevedo;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 2. Eliminación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Eliminación de bases de datos
DROP DATABASE IF EXISTS anitaquevedo_UNIVERSAL CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS anitaquevedo_UNIVERSAL LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_UNIVERSAL';

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 4. Tunning
-- 
-- -------------------------------------------------------------------------------------------------------

-- Compresión
SET hive.exec.compress.output=true;
SET parquet.compression=SNAPPY;

-- Particionamiendo dinámico
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 5. Despliegue de tabla PERSONA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_UNIVERSAL.PERSONA(
    ID STRING,
    NOMBRE STRING,
    TELEFONO STRING,
    CORREO STRING,
    FECHA_INGRESO STRING,
    EDAD INT,
    SALARIO DOUBLE,
    ID_EMPRESA STRING
)
STORED AS PARQUET
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_UNIVERSAL/PERSONA'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'parquet.compression'='SNAPPY'
);

-- Inserción, casteo de datos y aplicacion de reglas de limpieza
INSERT INTO TABLE anitaquevedo_UNIVERSAL.PERSONA
    SELECT
        CAST(T.ID AS STRING),
        CAST(T.NOMBRE AS STRING),
        CAST(T.TELEFONO AS STRING),
        CAST(T.CORREO AS STRING),
        CAST(T.FECHA_INGRESO AS STRING),
        CAST(T.EDAD AS INT),
        CAST(T.SALARIO AS DOUBLE),
        CAST(T.ID_EMPRESA AS STRING)
    FROM 
        anitaquevedo_LANDING.PERSONA T
    WHERE 
        T.ID IS NOT NULL AND
        T.ID_EMPRESA IS NOT NULL AND
        CAST(T.EDAD AS INT) > 0 AND
        CAST(T.EDAD AS INT) < 100 AND
        CAST(T.SALARIO AS DOUBLE) > 0 AND
        CAST(T.SALARIO AS DOUBLE) < 10000000;

-- Impresión de datos
SELECT * FROM anitaquevedo_UNIVERSAL.PERSONA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 6. Despliegue de tabla EMPRESA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_UNIVERSAL.EMPRESA(
    ID STRING,
    NOMBRE STRING
)
STORED AS PARQUET
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_UNIVERSAL/EMPRESA'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'parquet.compression'='SNAPPY'
);

-- Inserción, casteo de datos y aplicacion de reglas de limpieza
INSERT INTO TABLE anitaquevedo_UNIVERSAL.EMPRESA
    SELECT
        CAST(T.ID AS STRING),
        CAST(T.NOMBRE AS STRING)
    FROM 
        anitaquevedo_LANDING.EMPRESA T
    WHERE 
        T.ID IS NOT NULL; 

-- Impresión de datos
SELECT * FROM anitaquevedo_UNIVERSAL.EMPRESA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 7. Despliegue de tabla TRANSACCION
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_UNIVERSAL.TRANSACCION(
    ID_PERSONA STRING,
    ID_EMPRESA STRING,
    MONTO DOUBLE
)
PARTITIONED BY (FECHA STRING)
STORED AS PARQUET
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_UNIVERSAL/TRANSACCION'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'parquet.compression'='SNAPPY'
);

-- Inserción por particionamiento dinámico, casteo de datos y aplicacion de reglas de limpieza
INSERT INTO TABLE anitaquevedo_UNIVERSAL.TRANSACCION
PARTITION(FECHA)
    SELECT
        CAST(T.ID_PERSONA AS STRING),
        CAST(T.ID_EMPRESA AS STRING),
        CAST(T.MONTO AS DOUBLE),
        CAST(T.FECHA AS STRING)
    FROM 
        anitaquevedo_LANDING.TRANSACCION T
    WHERE 
        T.ID_PERSONA IS NOT NULL AND
        T.ID_EMPRESA IS NOT NULL AND
        CAST(T.MONTO AS DOUBLE) >= 0;

-- Impresión de datos
SELECT * FROM anitaquevedo_UNIVERSAL.TRANSACCION LIMIT 10;

-- Verificamos las particiones
SHOW PARTITIONS anitaquevedo_UNIVERSAL.TRANSACCION;