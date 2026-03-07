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
DROP DATABASE IF EXISTS anitaquevedo_LANDING CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS anitaquevedo_LANDING LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING';


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
CREATE TABLE anitaquevedo_LANDING.PERSONA
STORED AS AVRO
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING/persona'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/anitaquevedo/ejercicio2/schema/anitaquevedo_LANDING/persona.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE anitaquevedo_LANDING.PERSONA
SELECT * FROM  anitaquevedo_LANDING_TMP.PERSONA;

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING.PERSONA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 6. Despliegue de tabla EMPRESA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_LANDING.EMPRESA
STORED AS AVRO
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING/empresa'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/anitaquevedo/ejercicio2/schema/anitaquevedo_LANDING/empresa.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos
INSERT INTO TABLE anitaquevedo_LANDING.EMPRESA
SELECT * FROM  anitaquevedo_LANDING_TMP.EMPRESA;  

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING.EMPRESA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 7. Despliegue de tabla TRANSACCION
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_LANDING.TRANSACCION
PARTITIONED BY (FECHA STRING)
STORED AS AVRO
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING/transaccion'
TBLPROPERTIES(
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1',
    'avro.schema.url'='/user/anitaquevedo/ejercicio2/schema/anitaquevedo_LANDING/transaccion.avsc',
	'avro.output.codec'='snappy'
);

-- Inserción de datos por particionamiento dinámico
INSERT INTO TABLE anitaquevedo_LANDING.TRANSACCION
PARTITION(FECHA)
SELECT * FROM  anitaquevedo_LANDING_TMP.TRANSACCION;

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING.TRANSACCION LIMIT 10;

-- Verificamos las particiones
SHOW PARTITIONS anitaquevedo_LANDING.TRANSACCION;