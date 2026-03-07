##########################################################################################################
##
## @copyright Anita Quevedo
##
##########################################################################################################

##########################################################################################################
##
## @section 1. Listado de carpetas
## sh nombrearchivo.sh
##########################################################################################################

#Listamos la raíz del sistema de archivos distribuidos
hdfs dfs -ls /

#Listamos   las carpetas
hdfs dfs -ls /



#Listamos la carpeta "user"
#En esta carpeta cada usuario tiene una carpeta para trabajar
hdfs dfs -ls /user

#Listamos nuestra
hdfs dfs -ls /user/


##########################################################################################################
##
## @section 2. Creacion de carpetas
##
##########################################################################################################

#Como cada uno de nosotros tenemos nuestro propio usuario crearemos una variable que almacene el nombre del usuario
export PARAM_USERNAME=sebastian

#Vemos el contenido de la variable
echo ${PARAM_USERNAME}

#Listamos nuestra carpeta de usuario usando la variable
hdfs dfs -ls /user/${PARAM_USERNAME}

#Creamos algunas carpetas mas
hdfs dfs -mkdir /user/${PARAM_USERNAME}/example/carpeta1
hdfs dfs -mkdir /user/${PARAM_USERNAME}/example/carpeta2
hdfs dfs -mkdir /user/${PARAM_USERNAME}/example/carpeta3

#Listamos la carpeta "example"
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Vamos a crear una estructura de carpetas anidadas dentro de example:
#
# - /user/${PARAM_USERNAME}
#	- carpeta1
#		- carpetaA
#			- carpetaB
#				- carpetaC

#Trataremos de ejecutar el comando de creación
hdfs dfs -mkdir /user/${PARAM_USERNAME}/example/carpeta1/carpetaA/carpetaB/carpetaC

#Obtendremos un error
#Agregaremos un parametro para creacion recursiva de carpetas
hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/example/carpeta1/carpetaA/carpetaB/carpetaC

#Verificamos
hdfs dfs -ls  -R /user/${PARAM_USERNAME}/example

##########################################################################################################
##
## @section 3. Creacion de archivos vacios
##
##########################################################################################################

#Creacion de un archivo vacio con extension
hdfs dfs -touchz /user/${PARAM_USERNAME}/example/archivo_vacio.txt

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Creacion de un archivo vacio sin extension
hdfs dfs -touchz /user/${PARAM_USERNAME}/example/archivo_vacio_sin_extension

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Creacion de un archivo vacio sin extension como un "flag" de proceso exitoso
hdfs dfs -touchz /user/${PARAM_USERNAME}/example/_SUCCESS

#Creacion de un archivo vacio sin extension como un "flag" de proceso con errores
hdfs dfs -touchz /user/${PARAM_USERNAME}/example/_ERROR

#Verificamos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

##########################################################################################################
##
## @section 4. Subida de archivos al cluster
##
##########################################################################################################

#Subir un archivo desde Linux a HDFS
hdfs dfs -put archivos/persona.data /user/${PARAM_USERNAME}/example

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example/

#Vemos el contenido del archivo
hdfs dfs -cat /user/${PARAM_USERNAME}/example/persona.data

#Vemos solo algunos registros del archivo
hdfs dfs -tail /user/${PARAM_USERNAME}/example/persona.data

#Subir archivos que cumplan un patrón, desde Linux a HDFS
hdfs dfs -put archivos/transacciones*.data /user/${PARAM_USERNAME}/example

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

##########################################################################################################
##
## @section 5. Eliminando recursos
##
##########################################################################################################

#Eliminando un archivo
hdfs dfs -rm -f /user/${PARAM_USERNAME}/example/persona.data

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Eliminando recursos que cumpla un patrón
hdfs dfs -rm -f /user/${PARAM_USERNAME}/example/transacciones*.data

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Eliminando una carpeta y su contenido recursivamente
hdfs dfs -rm -r -f /user/${PARAM_USERNAME}/example/carpeta1

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Es importante saber que los archivos son enviados al "trash", el cual es como una "papelera de reciclaje".
hdfs dfs -ls /user/${PARAM_USERNAME}/

#Dentro estan los archivos borrados
hdfs dfs -ls -R /user/${PARAM_USERNAME}/.Trash

#Para recuperar un archivo lo movemos
#hdfs dfs -mv /user/${PARAM_USERNAME}/.Trash/Current/user/${PARAM_USERNAME}/example/persona.data /user/${PARAM_USERNAME}/example

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Para borrar los archivos de manera permanente debemos vaciar esta papelera
#hdfs dfs -rm -r -f /user/${PARAM_USERNAME}/.Trash/*
