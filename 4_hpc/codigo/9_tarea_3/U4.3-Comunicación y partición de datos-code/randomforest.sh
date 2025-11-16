#!/bin/bash
#SBATCH --job-name=randomforest             # Nombre del trabajo
#SBATCH --output=randomforest_N8_%j.log            # Archivo de salida (%j = job ID)
#SBATCH --error=error_%j.log              # Archivo de error
#SBATCH --time=00:10:00                   # Tiempo máximo de ejecución (HH:MM:SS)
#SBATCH --nodes=1                         # Número de nodos
#SBATCH --ntasks=2                      # Número total de tareas
#SBATCH --cpus-per-task=1              # Núcleos por tarea

# Cargar modulos si es necesario
module load python3
module swap openmpi4 mpich/3.4.3-ofi
module load py3-mpi4py

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
# Comando principal que quieres ejecutar
#python3.6 random_forest_joblib.py
#mpiexec -n $SLURM_NTASKS python3.6 random_forest_mpi.py
mpiexec -n $SLURM_NTASKS python3.6 random_forest_hybrid.py

module unload python3
module unload openmpi4 mpich/3.4.3-ofi
module unload py3-mpi4py
