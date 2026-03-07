#!/bin/bash

##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

#COMANDO DE EJECUCION
#bash Laboratorio_019_execute_all.sh "sebastian"

##########################################################################################################
#
# @section 1. Definición de parámetros
#
##########################################################################################################

#Creamos una variable en HADOOP
export PARAM_USERNAME=$1

##########################################################################################################
#
# @section 2. Ejecución de scripts
#
##########################################################################################################

echo "Ejecutando deploy de arbol de directorios..."
. ./Laboratorio_014_deploy.sh "${PARAM_USERNAME}"

echo "Desplegando landing_tmp..."
sed "s/__PARAM_USERNAME__/${PARAM_USERNAME}/g" Laboratorio_015_deploy_database_landing_tmp.sql > /tmp/_015_tmp.sql
beeline -u jdbc:hive2:// -f /tmp/_015_tmp.sql
rm -f /tmp/_015_tmp.sql

echo "Desplegando landing..."
sed "s/__PARAM_USERNAME__/${PARAM_USERNAME}/g" Laboratorio_016_deploy_database_landing.sql > /tmp/_016_tmp.sql
beeline -u jdbc:hive2:// -f /tmp/_016_tmp.sql
rm -f /tmp/_016_tmp.sql

echo "Desplegando universal..."
sed "s/__PARAM_USERNAME__/${PARAM_USERNAME}/g" Laboratorio_017_deploy_database_universal.sql > /tmp/_017_tmp.sql
beeline -u jdbc:hive2:// -f /tmp/_017_tmp.sql
rm -f /tmp/_017_tmp.sql

echo "Desplegando smart..."
sed "s/__PARAM_USERNAME__/${PARAM_USERNAME}/g" Laboratorio_018_deploy_database_smart.sql > /tmp/_018_tmp.sql
beeline -u jdbc:hive2:// -f /tmp/_018_tmp.sql
rm -f /tmp/_018_tmp.sql