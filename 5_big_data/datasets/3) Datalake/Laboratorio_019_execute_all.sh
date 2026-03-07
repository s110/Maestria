#!/bin/bash

##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

#COMANDO DE EJECUCION
#sh Laboratorio_019_execute_all.sh "anitaquevedo"

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
source Laboratorio_014_deploy.sh "${PARAM_USERNAME}"

echo "Desplegando landing_tmp..."
beeline -u jdbc:hive2:// -f Laboratorio_015_deploy_database_landing_tmp.sql --hiveconf "PARAM_USERNAME=${PARAM_USERNAME}"

echo "Desplegando landing..."
beeline -u jdbc:hive2:// -f Laboratorio_016_deploy_database_landing.sql --hiveconf "PARAM_USERNAME=${PARAM_USERNAME}"

echo "Desplegando universal..."
beeline -u jdbc:hive2:// -f Laboratorio_017_deploy_database_universal.sql --hiveconf "PARAM_USERNAME=${PARAM_USERNAME}"

echo "Desplegando smart..."
beeline -u jdbc:hive2:// -f Laboratorio_018_deploy_database_smart.sql --hiveconf "PARAM_USERNAME=${PARAM_USERNAME}"