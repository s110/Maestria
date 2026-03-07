#!/bin/bash

#COMANDO DE EJECUCION
#sh Laboratorio_006_Permisos.sh "anitaquevedo"

##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

#Definimos las variables
export PARAM_USERNAME=$1

#Asignar permisos
echo "Asignando permisos..."
#hdfs dfs -chown usuario5:grupoA /user/${PARAM_USERNAME}/ejercicio1/data1/file.txt
hdfs dfs -chmod 755 /user/${PARAM_USERNAME}/ejercicio1/data1/file.txt
hdfs dfs -chmod 700 /user/${PARAM_USERNAME}/ejercicio1/data1/titanic.csv
#hdfs dfs -chown -R usuario2:grupoK /user/${PARAM_USERNAME}/ejercicio1/data2
hdfs dfs -chmod -R 777 /user/${PARAM_USERNAME}/ejercicio1/data2

#Verificamos
echo "Listando..."
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio1