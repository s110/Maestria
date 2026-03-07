-- -------------------------------------------------------------------------------------------------------
-- 
-- @copyright Anita Quevedo
-- 
-- -------------------------------------------------------------------------------------------------------

-- COMANDO DE EJECUCION
-- beeline -u jdbc:hive2:// -f Laboratorio_015_deploy_database_landing_tmp.sql --hiveconf "PARAM_USERNAME=anitaquevedo"

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
DROP DATABASE IF EXISTS anitaquevedo_LANDING_TMP CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS anitaquevedo_LANDING_TMP LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING_TMP';

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 4. Despliegue de tabla PERSONA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_LANDING_TMP.PERSONA(
	ID STRING,
	NOMBRE STRING,
	TELEFONO STRING,
	CORREO STRING,
	FECHA_INGRESO STRING,
	EDAD STRING,
	SALARIO STRING,
	ID_EMPRESA STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING_TMP/persona'
TBLPROPERTIES(
    'skip.header.line.count'='1',
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1'
);

-- Subida de datos
LOAD DATA LOCAL INPATH 'persona.data'
INTO TABLE anitaquevedo_LANDING_TMP.PERSONA;

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING_TMP.PERSONA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 5. Despliegue de tabla EMPRESA
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_LANDING_TMP.EMPRESA(
	ID STRING,
	NOMBRE STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING_TMP/empresa'
TBLPROPERTIES(
    'skip.header.line.count'='1',
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1'
);

-- Subida de datos
LOAD DATA LOCAL INPATH 'empresa.data'
INTO TABLE anitaquevedo_LANDING_TMP.EMPRESA;

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING_TMP.EMPRESA LIMIT 10;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 6. Despliegue de tabla TRANSACCION
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de tabla
CREATE TABLE anitaquevedo_LANDING_TMP.TRANSACCION(
	ID_PERSONA STRING,
	ID_EMPRESA STRING,
	MONTO STRING,
	FECHA STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION '/user/anitaquevedo/ejercicio2/database/anitaquevedo_LANDING_TMP/transaccion'
TBLPROPERTIES(
    'skip.header.line.count'='1',
    'store.charset'='ISO-8859-1', 
    'retrieve.charset'='ISO-8859-1'
);

-- Subida de datos
LOAD DATA LOCAL INPATH 'transacciones.data'
INTO TABLE anitaquevedo_LANDING_TMP.TRANSACCION;

-- Impresión de datos
SELECT * FROM anitaquevedo_LANDING_TMP.TRANSACCION LIMIT 10;