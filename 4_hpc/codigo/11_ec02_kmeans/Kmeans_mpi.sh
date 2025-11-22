#!/bin/bash
#SBATCH --job-name=kmeans_mpi
#SBATCH --output=logs/kmeans_%A_%a.out
#SBATCH --error=logs/kmeans_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks=8            # número de procesos MPI
#SBATCH --time=00:10:00
#SBATCH --partition=standard
#SBATCH --array=1,2,3,4,5,6     # 6 tamaños diferentes

# ---------------------------
# LISTA DE N PARA SCALING
# ---------------------------
N_VALUES=(32768 65536 131072 262144 524288 1048576)
module load python3
module load py3-mpi4py
module load py3-scipy
module load py3-numpy

# Elegir N según el array ID
N=${N_VALUES[$SLURM_ARRAY_TASK_ID-1]}

echo "Ejecutando con N = $N"

# Activar entorno, si lo usas
# source activate myenv

# Exportar N al programa MPI
export KMEANS_N=$N

# Ejecutar el código MPI
mpirun -np $SLURM_NTASKS python3.6 Kmeans_mpi.py

