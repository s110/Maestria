-- -------------------------------------------------------------------------------------------------------
-- 
-- @copyright Anita Quevedo
-- 
-- -------------------------------------------------------------------------------------------------------

-- COMANDO DE EJECUCION
-- beeline -u jdbc:hive2:// -f Laboratorio_018_deploy_database_smart.sql --hivevar "PARAM_USERNAME=anitaquevedo"

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
DROP DATABASE IF EXISTS __PARAM_USERNAME___SMART CASCADE;

-- -------------------------------------------------------------------------------------------------------
-- 
-- @section 3. Creación de base de datos
-- 
-- -------------------------------------------------------------------------------------------------------

-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS __PARAM_USERNAME___SMART LOCATION '/user/__PARAM_USERNAME__/ejercicio2/database/__PARAM_USERNAME___SMART';
