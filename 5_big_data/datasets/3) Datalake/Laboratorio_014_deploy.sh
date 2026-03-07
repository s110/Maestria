#!/bin/bash

##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

#COMANDO DE EJECUCION
#sh Laboratorio_014_deploy.sh "anitaquevedo"  

##########################################################################################################
#
# @section 1. Definición de parámetros
#
##########################################################################################################

#Creamos una variable en HADOOP
export PARAM_USERNAME=$1


##########################################################################################################
#
# @section 2. Creación de carpeta de estructura de carpetas
#
##########################################################################################################

#Eliminamos la carpeta si existe
echo "Eliminando la carpeta..."
hdfs dfs -rm -r -f /user/${PARAM_USERNAME}/ejercicio2

#Estructura de carpetas para "landing_tmp"
echo "Creando la estructura de carpetas para landing_tmp..."
hdfs dfs -mkdir -p \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING_TMP \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING_TMP/persona \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING_TMP/empresa \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING_TMP/transaccion

#Estructura de carpetas para "landing"
echo "Creando la estructura de carpetas para landing..."
hdfs dfs -mkdir -p \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING/persona \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING/empresa \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_LANDING/transaccion \
/user/${PARAM_USERNAME}/ejercicio2/schema/${PARAM_USERNAME}_LANDING

#Estructura de carpetas para "universal"
echo "Creando la estructura de carpetas para universal..."
hdfs dfs -mkdir -p \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_UNIVERSAL \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_UNIVERSAL/persona \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_UNIVERSAL/empresa \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_UNIVERSAL/transaccion \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_UNIVERSAL/transaccion_enriquecida

#Estructura de carpetas para "smart"
echo "Creando la estructura de carpetas para smart..."
hdfs dfs -mkdir -p \
/user/${PARAM_USERNAME}/ejercicio2/database/${PARAM_USERNAME}_SMART

#Subida de archivos de "schema"
hdfs dfs -put persona.avsc  /user/${PARAM_USERNAME}/ejercicio2/schema/${PARAM_USERNAME}_LANDING/persona.avsc
hdfs dfs -put empresa.avsc  /user/${PARAM_USERNAME}/ejercicio2/schema/${PARAM_USERNAME}_LANDING/empresa.avsc
hdfs dfs -put transaccion.avsc  /user/${PARAM_USERNAME}/ejercicio2/schema/${PARAM_USERNAME}_LANDING/transaccion.avsc


#Listado de arbol de directorios
echo "Listando arbol de directorios..."
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio2


