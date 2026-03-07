##########################################################################################################
###
 # @section 1. Definicion de parametros
 ##
##########################################################################################################

#Definimos el nombre de nuestro usuario
export PARAM_USERNAME=sebastian

##########################################################################################################
###
 # @section 2. Permisos ACL
 ##
##########################################################################################################

#Hemos aprendido a cambiar los usuarios dueños y los grupos dueños de los recursos, también a asignarles permisos de lectura, escritura y ejecución, pero ¿cómo podemos dar permisos de este tipo?:
#
# -	El usuario "usuarioA" tenga permisos de sólo lectura al recurso "carpeta_acl"
# -	El usuario "usuarioB" tenga permisos de lectura y escritura al recurso "carpeta_acl"
# -	El usuario "usuarioC" tenga permisos de lectura, escritura y ejecución al recurso "carpeta_acl"
# -	El grupo "grupoK" tenga permisos de sólo lectura al recurso "carpeta_acl"
#
#Podemos hacerlo por medio de los permisos ACL

#Si no existe la carpeta, la creamos la carpeta a la que le asignaremos permisos
hdfs dfs -mkdir -p /user/${PARAM_USERNAME}/example2/carpeta_acl

#El usuario "usuarioA" tenga permisos de sólo lectura al recurso "carpeta2"
hdfs dfs -setfacl -R -m user:usuarioA:r-- /user/${PARAM_USERNAME}/example2/carpeta_acl

#Consultamos los permisos ACL
hdfs dfs -getfacl /user/${PARAM_USERNAME}/example2/carpeta_acl

#Agregamos más permisos
hdfs dfs -setfacl -R -m user:usuarioB:rw- /user/${PARAM_USERNAME}/example2/carpeta_acl
hdfs dfs -setfacl -R -m user:usuarioC:rwx /user/${PARAM_USERNAME}/example2/carpeta_acl
hdfs dfs -setfacl -R -m group:grupoK:r-- /user/${PARAM_USERNAME}/example2/carpeta_acl

#Verificamos
hdfs dfs -getfacl /user/${PARAM_USERNAME}/example2/carpeta_acl

#Remover un usuario de los permisos
hdfs dfs -setfacl -x user:usuarioA /user/${PARAM_USERNAME}/example2/carpeta_acl

#Verificamos
hdfs dfs -getfacl /user/${PARAM_USERNAME}/example2/carpeta_acl

##########################################################################################################
###
 # @section 3. Permisos ACL a futuro
 ##
##########################################################################################################

#Sabemos que con el parámetro "-R" se aplican los permisos a los objetos contenidos en el directorio
#pero ¿qué pasa con los nuevos archivos y carpetas que se creen? Estos no heredarán estos permisos.
#Para poder asignar a los futuros archivos y carpetas los permisos, debemos ejecutar estos dos comandos:

#El usuario "usuarioA" tiene permiso a todos los archivos y carpetas que existen en este momento dentro de "carpeta_acl"
hdfs dfs -setfacl -R -m user:usuarioA:r-- /user/${PARAM_USERNAME}/example2/carpeta_acl

#El usuario "usuarioA" tiene permiso a todos los archivos y carpetas que se creen en el futuro dentro de "carpeta_acl"
hdfs dfs -setfacl -R -m default:user:usuarioA:r-- /user/${PARAM_USERNAME}/example2/carpeta_acl

##########################################################################################################
###
 # @section 4. Verificando la integridad de los datos
 ##
##########################################################################################################

#Cuando hacemos transferencia de archivos existe la posibilidad de que se pierdan algunos bits.
#¿Cómo podemos garantizar que todos los bits se hayan almacenado correctamente?, por medio de un proceso de checksum

#Subimos un archivo
hdfs dfs -put ~/dataset/persona.data /user/${PARAM_USERNAME}/example2

#Verificamos el checksum del archivo origen en el GATEWAY
cksum ~/dataset/persona.data

#Verificamos el checksum del archivo destino en HDFS
hdfs dfs -cat /user/${PARAM_USERNAME}/example2/persona.data | cksum

##########################################################################################################
###
 # @section 5. Listando pesos recursivamente
 ##
##########################################################################################################

#Podemos listar el contenido de una carpeta y su peso recursivamente
hdfs dfs -du -s -h /user/spark

#También podemos listar el peso de cada directorio dentro de un directorio
hdfs dfs -du -s -h "/*"

##########################################################################################################
###
 # @section 6. Modificando el número de réplicas
 ##
##########################################################################################################

#Podemos aumentar o disminuir el número de réplicas de todos los archivos dentro de una carpeta
hdfs dfs -setrep -R -w 5 /user/${PARAM_USERNAME}/example2

#Verificamos
hdfs dfs -ls /user/${PARAM_USERNAME}/example2

##########################################################################################################
###
 # @section 6. Modificando el tamaño de bloque
 ##
##########################################################################################################

#Por defecto el tamaño de bloque de un archivo almacenado sobre HDFS es de 128MB.
#Si estamos guardando archivos muy pequeños (p.e., de 10 MB) no tiene sentido guardarlo en un tamaño de bloque tan grande.
#Para esto al momento de subir el archivo podemos guardarlo indicando el tamaño de bloque.
#IMPORTANTE: El tamaño de bloque sólo puede definirse al hacer el "put", una vez escrito no se puede modificar.
#El tamaño de bloque es indicado en bytes.

#Subimos un archivo indicando un tamaño de bloque de aproximadamente 10MB
#Obtendremos un error debido al tamaño mínimo de bloque configurado en la infraestructura
hdfs dfs -D dfs.blocksize=1000000 -put ~/dataset/empresa.data /user/${PARAM_USERNAME}/example2

#Aumentamos el tamaño de bloque
#Obtendremos otro error
hdfs dfs -D dfs.blocksize=1050000 -put ~/dataset/empresa.data /user/${PARAM_USERNAME}/example2

#Subimos un archivo indicando un tamaño de bloque
hdfs dfs -D dfs.blocksize=1050624 -put ~/dataset/empresa.data /user/${PARAM_USERNAME}/example2

#Consultamos el tamaño de bloque del archivo
hadoop fs -stat %o /user/${PARAM_USERNAME}/example2/empresa.data
