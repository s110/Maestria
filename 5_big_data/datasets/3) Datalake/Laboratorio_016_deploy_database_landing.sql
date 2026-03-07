-- -------------------------------------------------------------------------------------------------------
-- 
-- @copyright Anita Quevedo
-- 
-- -------------------------------------------------------------------------------------------------------

-- COMANDO DE EJECUCION
-- beeline -u jdbc:hive2:// -f Laboratorio_016_deploy_database_landing.sql --hivevar "PARAM_USERNAME=anitaquevedo"

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
DROP DATABASE IF EXISTS __PARAM_USERNAME___LANDING CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS __PARAM_USERNAME___LANDING LOCATION '/user/__PARAM_USERNAME__/ejercicio2/database/__PARAM_USERNAME___LANDING';

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 4. Tunning
-- 
-- -------------------------------------------------------------------------------------------------------

-- Compresión
SET hive.exec.compress.output=true;
SET avro.output.codec=snappy;

-- Particionamiendo dinámico
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 5. Despliegue de tabla PERSONA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE __PARAM_USERNAME___LANDING.PERSONA
STORED AS AVRO
LOCATION '/user/__PARAM_USERNAME__/ejercicio2/database/__PARAM_USERNAME___LANDING/persona'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1',
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/__PARAM_USERNAME__/ejercicio2/schema/__PARAM_USERNAME___LANDING/persona.avsc',
    'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE __PARAM_USERNAME___LANDING.PERSONA
SELECT * FROM  __PARAM_USERNAME___LANDING_TMP.PERSONA;

-- Impresión de datos
SELECT * FROM __PARAM_USERNAME___LANDING.PERSONA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 6. Despliegue de tabla EMPRESA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE __PARAM_USERNAME___LANDING.EMPRESA
STORED AS AVRO
LOCATION '/user/__PARAM_USERNAME__/ejercicio2/database/__PARAM_USERNAME___LANDING/empresa'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1',
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/__PARAM_USERNAME__/ejercicio2/schema/__PARAM_USERNAME___LANDING/empresa.avsc',
    'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE __PARAM_USERNAME___LANDING.EMPRESA
SELECT * FROM  __PARAM_USERNAME___LANDING_TMP.EMPRESA;

-- Impresión de datos
SELECT * FROM __PARAM_USERNAME___LANDING.EMPRESA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 7. Despliegue de tabla TRANSACCION
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE __PARAM_USERNAME___LANDING.TRANSACCION
PARTITIONED BY (FECHA STRING)
STORED AS AVRO
LOCATION '/user/__PARAM_USERNAME__/ejercicio2/database/__PARAM_USERNAME___LANDING/transaccion'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1',
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/__PARAM_USERNAME__/ejercicio2/schema/__PARAM_USERNAME___LANDING/transaccion.avsc',
    'avro.output.codec'='snappy'
);

-- Inserción de datos por particionamiento dinámico
INSERT INTO TABLE __PARAM_USERNAME___LANDING.TRANSACCION
PARTITION(FECHA)
SELECT * FROM  __PARAM_USERNAME___LANDING_TMP.TRANSACCION;

-- Impresión de datos
SELECT * FROM __PARAM_USERNAME___LANDING.TRANSACCION LIMIT 10;

-- Verificamos las particiones
SHOW PARTITIONS __PARAM_USERNAME___LANDING.TRANSACCION;