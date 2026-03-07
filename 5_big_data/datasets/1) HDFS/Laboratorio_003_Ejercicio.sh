##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

##########################################################################################################
##
## @section 1. Descripcion del ejercicio
##
##########################################################################################################

#Crear dentro de HDFS en tu carpeta de usuario la siguiente estructura de carpetas
#
#/user/${PARAM_USERNAME}
#   ejercicio1
#      carpeta1
#         subcarpeta1
#            persona.data
#         subcarpeta2
#         subcarpeta3
#      carpeta2
#         empresa.data
#      carpeta3
#      data1
#         titanic.csv (archivo subido desde tu computadora, permisos: usuario5:grupoA 755)
#         voidfile.txt (archivo vacio, permisos 700)
#      data2 (permisos recursivos: usuario2:grupoK 777)
#         2017-01-27
#            titanic.csv (archivo subido desde tu computadora)
#         2017-01-28
#            titanic.csv (archivo subido desde tu computadora)
#         2017-01-29
#      data3

##########################################################################################################
##
## @section 2. Solucion
##
##########################################################################################################

#Definimos las variables
export PARAM_USERNAME=anitaquevedo

#Creamos la carpeta del ejercicio
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1

#Creamos la estructura de carpetas
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta1
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta2
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta3
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data1
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data2
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data3
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta1
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta2
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta3
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-27
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-28
hdfs dfs -mkdir /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-29

#Verificamos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio1

#Subimos los archivos
hdfs dfs -put persona.data /user/${PARAM_USERNAME}/ejercicio1/carpeta1/subcarpeta1
hdfs dfs -put empresa.data /user/${PARAM_USERNAME}/ejercicio1/carpeta2
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data1
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-27
hdfs dfs -put titanic.csv /user/${PARAM_USERNAME}/ejercicio1/data2/2017-01-28
hdfs dfs -touchz /user/${PARAM_USERNAME}/ejercicio1/data1/voidfile.txt

#Verificamos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio1

#Logearse con el super hdfs
#su hdfs
#si quisieras configurar: https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/security?hl=es-419#gcloud-command_1

#Asignar permisos

#hdfs dfs -chown usuario5:grupoA /user/${PARAM_USERNAME}/ejercicio1/data1/titanic.csv
hdfs dfs -chmod 755 /user/${PARAM_USERNAME}/ejercicio1/data1/titanic.csv
hdfs dfs -chmod 700 /user/${PARAM_USERNAME}/ejercicio1/data1/voidfile.txt
#hdfs dfs -chown -R usuario2:grupoK /user/${PARAM_USERNAME}/ejercicio1/data2
hdfs dfs -chmod -R 777 /user/${PARAM_USERNAME}/ejercicio1/data2

#Verificamos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/ejercicio1

#Salimos del super-usuario
exit