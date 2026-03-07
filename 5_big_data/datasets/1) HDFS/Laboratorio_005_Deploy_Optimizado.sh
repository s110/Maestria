#!/bin/bash

#COMANDO DE EJECUCION
#sh Laboratorio_005_Deploy_Optimizado.sh "anitaquevedo"

##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

#Definimos las variables
export PARAM_USERNAME=$1

#Eliminamos la carpeta del ejercicio
echo "Eliminando carpeta del ejercicio..."
hdfs dfs -rm -r -f /user/${PARAM_USERNAME}/ejercicio1

#Creamos la carpeta del ejercicio
echo "Creando carpeta del ejercicio..."
hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/ejercicio1

#Creamos la estructura de carpetas
echo "Creando estructura de carpetas..."
hdfs dfs -mkdir \
/user/${PARAM_USERNAME}/ejercicio1/carpeta1 \
/user/${PARAM_USERNAME}/ejercicio1/carpeta2 \
/user/${PARAM_USERNAME}/ejercicio1/carpeta3 \
/user/${PARAM_USERNAME}/ejercicio1/data1 \
/user/${PARAM_USERNAME}/ejercicio1/data2 \
/user/${PARAM_USERNAME}/ejercicio1/data3 \
/user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta1 \
/user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta2 \
/user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta3 \
/user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-27 \
/user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-28 \
/user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-29

#Subimos los archivos
echo "Subiendo archivos..."
hdfs dfs -put persona.data /user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta1
hdfs dfs -put empresa.data /user/${PARAM_USERNAME}/ejercicio1/carpeta2
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data1
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-27
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-28
hdfs dfs -touchz /user/${PARAM_USERNAME}/ejercicio1/data1/voidfile.txt

#Verificamos
echo "Listando..."
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio1