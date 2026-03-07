-- -------------------------------------------------------------------------------------------------------
-- 
-- @copyright Anita Quevedo
-- 
-- -------------------------------------------------------------------------------------------------------

-- COMANDO DE EJECUCION
-- beeline -u jdbc:hive2:// -f Laboratorio_016_deploy_database_landing.sql --hiveconf "PARAM_USERNAME=anitaquevedo"

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
DROP DATABASE IF EXISTS ${hiveconf:PARAM_USERNAME}_LANDING CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS ${hiveconf:PARAM_USERNAME}_LANDING LOCATION '/user/${hiveconf:PARAM_USERNAME}/ejercicio2/database/${hiveconf:PARAM_USERNAME}_LANDING';


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
CREATE TABLE ${hiveconf:PARAM_USERNAME}_LANDING.PERSONA
STORED AS AVRO
LOCATION '/user/${hiveconf:PARAM_USERNAME}/ejercicio2/database/${hiveconf:PARAM_USERNAME}_LANDING/persona'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/${hiveconf:PARAM_USERNAME}/ejercicio2/schema/${hiveconf:PARAM_USERNAME}_LANDING/persona.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE ${hiveconf:PARAM_USERNAME}_LANDING.PERSONA
SELECT * FROM  ${hiveconf:PARAM_USERNAME}_LANDING_TMP.PERSONA;

-- Impresión de datos
SELECT * FROM ${hiveconf:PARAM_USERNAME}_LANDING.PERSONA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 6. Despliegue de tabla EMPRESA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE ${hiveconf:PARAM_USERNAME}_LANDING.EMPRESA
STORED AS AVRO
LOCATION '/user/${hiveconf:PARAM_USERNAME}/ejercicio2/database/${hiveconf:PARAM_USERNAME}_LANDING/empresa'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/${hiveconf:PARAM_USERNAME}/ejercicio2/schema/${hiveconf:PARAM_USERNAME}_LANDING/empresa.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE ${hiveconf:PARAM_USERNAME}_LANDING.EMPRESA
SELECT * FROM  ${hiveconf:PARAM_USERNAME}_LANDING_TMP.EMPRESA;  

-- Impresión de datos
SELECT * FROM ${hiveconf:PARAM_USERNAME}_LANDING.EMPRESA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 7. Despliegue de tabla TRANSACCION
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE ${hiveconf:PARAM_USERNAME}_LANDING.TRANSACCION
PARTITIONED BY (FECHA STRING)
STORED AS AVRO
LOCATION '/user/${hiveconf:PARAM_USERNAME}/ejercicio2/database/${hiveconf:PARAM_USERNAME}_LANDING/transaccion'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/${hiveconf:PARAM_USERNAME}/ejercicio2/schema/${hiveconf:PARAM_USERNAME}_LANDING/transaccion.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos por particionamiento dinámico
INSERT INTO TABLE ${hiveconf:PARAM_USERNAME}_LANDING.TRANSACCION
PARTITION(FECHA)
SELECT * FROM  ${hiveconf:PARAM_USERNAME}_LANDING_TMP.TRANSACCION;

-- Impresión de datos
SELECT * FROM ${hiveconf:PARAM_USERNAME}_LANDING.TRANSACCION LIMIT 10;

-- Verificamos las particiones
SHOW PARTITIONS ${hiveconf:PARAM_USERNAME}_LANDING.TRANSACCION;