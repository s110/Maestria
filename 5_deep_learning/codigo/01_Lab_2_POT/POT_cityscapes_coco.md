Requiero que modifiques el archivo pot_cityscapes_colab.py para que pueda ser ejecutado en un entorno de SSH (subire todos los archivos alli y los scripts y lo correre alli) dentro de un servidor que funciona con SLURM. Por favor, ten en cuenta que el dataset de Cityscapes esta en /home/s.lopezmedina/Maestria/5_deep_learning/datasets/cityscapes (leftImg8bit, gtCoarse, gtFine) y el dataset de COCO-2017 esta en /home/s.lopezmedina/Maestria/5_deep_learning/datasets/coco_dataset (aunque en ssh estara segun abajo, igual el cityscapes en su carpeta cityscapes). Por favor, ten en cuenta que el script debe ser capaz de entrenar el modelo con el dataset de Cityscapes y con el dataset de COCO-2017, en ejecuciones diferentes. 
El nodo del servidor tiene estas specs:
ds001
Especificaciones
Nombre 	ds001
Procesador 	Intel(R) Xeon(R) Gold 5418Y 2.0 GHz 24 cores por socket, 48 por nodo.
Gráficos 	NVIDIA RTX A6000 48 GB GDDR6
Memoria 	1TB DRAM DDR5 5600MHz
Red 	Infiniband Mellanox MT28908
La forma en que esta incluida el coco dataset en el ssh es asi:
[sebastian.lopez@khipu coco_dataset]$ ls -l
total 26423980
drwxrwxr-x. 2 sebastian.lopez sebastian.lopez        4096 Mar 28 07:21 annotations
-rw-rw-r--. 1 sebastian.lopez sebastian.lopez   252907541 Jul 10  2018 annotations_trainval2017.zip
drwxrwxr-x. 2 sebastian.lopez sebastian.lopez     1462272 Aug 31  2017 test2017
-rw-rw-r--. 1 sebastian.lopez sebastian.lopez  6646970404 Jul 10  2018 test2017.zip
drwxrwxr-x. 2 sebastian.lopez sebastian.lopez     4153344 Aug 31  2017 train2017
-rw-rw-r--. 1 sebastian.lopez sebastian.lopez 19336861798 Jul 11  2018 train2017.zip
drwxrwxr-x. 2 sebastian.lopez sebastian.lopez      167936 Aug 31  2017 val2017
-rw-rw-r--. 1 sebastian.lopez sebastian.lopez   815585330 Jul 11  2018 val2017.zip
preferiblemente, por temas de facilidad, trabaja directamente con los archivos descomprimidos, no con los .zip (si por alguna razon es mas facil con los zips, indicamelo)

Quiero que hagas grid search solo con un parametro adicional a lo que ya esta contemplado en el script, que es el de tamaño de imagen, varialo desde 224 px hasta 448 px con pasos de 112 px. Es decir, 224, 336, 448 y guarda tambien esos resultados.
Acuerdate que lo importante es guardar todo en logs: results.log y error.log 
No crees ningun grafico alla, que todo se haga aca.
Para  que tengas una idea de un trabajo del ciclo pasado en slurm, te adjunto el archivo slurm_lab_4_yolo.sbatch y lab_4_yolo_finetuning_script.py. No te bases enteramente en esos, pero usalos en caso no sepas como es la estructura.
Te adjunto available_modules.md para que veas que modulos estan disponibles en ese servidor, en caso fuera necesario, igual puedes indicar crear un entorno virtual para las dependencias de python.
Cuando me digas que instalar con pip, yo creare el venv alla e instalare manualmente todos los requerimientos que necesites.
Y estos son los parametros de mi cuenta:
[sebastian.lopez@khipu ~]$ myaccount
---------------------------------------------------------
Khipu account                                            
---------------------------------------------------------
User                 Account            Default          
-------------------- ------------------ -----------------
sebastian.lopez      postgrado          postgrado          

--------------------------------------------------------------
Account Limits                                                
--------------------------------------------------------------
Account           Resources                       TimeLimit   
----------------- ------------------------------- ------------
a-postgrado       cpu=32,gres/shard=8,mem=98G       08:00:00 

DISCLAIMER: Tu eres una computadora extremadamente poderosa, por lo que no debes tener esperar nunca por el termino de la ejecucion de la terminal. Si por alguna razon tienes que usarla, debido a que tu tienes problemas para leer la terminal, outputea los comandos que necesites leer a un archivo temporal y leelos desde alli. No te detengas por nada del mundo.