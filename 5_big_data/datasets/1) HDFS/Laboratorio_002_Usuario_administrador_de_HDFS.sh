##########################################################################################################
## 
## @copyright Anita Quevedo
## 
##########################################################################################################

##########################################################################################################
##
## @section 1. Definicion de parametros
##
##########################################################################################################

#Definimos el nombre de nuestro usuario
export PARAM_USERNAME=anitaquevedo

##########################################################################################################
##
## @section 2. El super usuario de HDFS
##
##########################################################################################################

#Así como Linux tiene su super-usuario "root" el cual puede manipular todo el contenido del servidor, 
#Hadoop tiene al super-usuario "hdfs", el cual puede manipular todo el sistema de archivos de HDFS
#El super-usuario hdfs se utilizar para realizar temas de administración sobre los recursos, por ejemplo, asignar permisos de usuario
#Iniciamos sesión con el super usuario
#su hdfs

#¡IMPORTANTE!
#Al cambiar de sesión de usuario, necesitamos redefinir nuestros variables
#Dependiendo de la version de Linux que usemos puede ser que la variable se libere al cambiar de usuario
echo ${PARAM_USERNAME}

#Volvemos a definir la variable
export PARAM_USERNAME=anitaquevedo

##########################################################################################################
##
## @section 3. Asignando un dueño a los recursos
##
##########################################################################################################

#Por defecto el usuario dueño y el grupo dueño de un recurso es la persona que lo crea, pero podemos modificar esto asignándole otro usuario


#crearusuario y grupousuario
sudo su

useradd usuario1
useradd usuario2
sudo groupadd grupo1
sudo groupadd grupo7
usermod -g grupo1 usuario1
usermod -g grupo7 usuario2


#Asignamos como nuevo dueño de "carpeta2" al usuario "usuario1"
#Asignamos como grupo asociado de "carpeta2" al grupo de usuarios "grupo1"
sudo passwd hdfs 

hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/example/carpeta2

hdfs dfs -chown usuario1:grupo1 /user/${PARAM_USERNAME}/example/carpeta2

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Asignamos como nuevo dueño de "carpeta3" al usuario "usuario1"
#Asignamos como grupo asociado de "carpeta3" al grupo de usuarios "grupo1"

hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/example/carpeta3
hdfs dfs -chown usuario2:grupo7 /user/${PARAM_USERNAME}/example/carpeta3

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example

#Vamos a crear una estructura de carpeta recursivas
hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/example/carpeta4/carpeta5/carpeta6

#Verificamos la estructura creada de manera recursiva
#Verificamos los permisos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

#Cambiamos los permisos de carpeta4
hdfs dfs -chown usuario1:grupo1 /user/${PARAM_USERNAME}/example/carpeta4

#hdfs dfs -chmod 777  /user/${PARAM_USERNAME}/example/carpeta4

#Verificamos los permisos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

#Cambiamos los permisos de carpeta4 de manera recursiva
hdfs dfs -chown -R usuario1:grupo1 /user/${PARAM_USERNAME}/example/carpeta4

#Verificamos los permisos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

##########################################################################################################
##
## @section 4. Asignando permisos de escritura, lectura y ejecucion
##
##########################################################################################################

# Podemos cambiar los permisos de lectura, escritura y ejecución de los recursos con el siguiente comando
#
# hdfs dfs -chmod DGO /path/to/resource
#
# Donde
# 
# - "D" son los permisos para el usuario dueño del recurso
# - "G" son los permisos para el grupo dueño del recurso
# - "O" son los permisos para el resto de usuarios
#
# "D", "G" y "O" deberán tomar alguno de estos valores:
#
# - 7: Permisos de lectura, escritura y ejecución (rwx)
# - 6: Permisos de lectura y escritura (rw-)
# - 5: Permisos de lectura y ejecución (r-x)
# - 4: Permisos de lectura (r--)
# - 1: Permisos de ejecución (--x)
# - 0: Sin ningún permiso (---)

#Cambiamos los permisos de acceso a "carpeta4"
hdfs dfs -chmod 750 /user/${PARAM_USERNAME}/example/carpeta4


#Verificamos los permisos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

#Cambiamos los permisos de acceso a "carpeta4" de manera recursiva
hdfs dfs -chmod -R 750 /user/${PARAM_USERNAME}/example/carpeta4

#Verificamos los permisos
hdfs dfs -ls -R /user/${PARAM_USERNAME}/example

##########################################################################################################
##
## @section 5. Cerrar sesión del super-usuario
##
##########################################################################################################

#Salimos de la sesion del super-usuario
exit