#!/bin/bash
#SBATCH -J pi-mpi              # Nombre del job
#SBATCH -o logs_py/%x.%j.out      # Stdout (%x=jobname, %j=jobid)
#SBATCH -e logs_py/%x.%j.err      # Stderr
#SBATCH -p standard            # partición
#SBATCH -N 1                   # Nodos (puedes subir si quieres multinodo)
#SBATCH -n 32                   # Tareas MPI (procesos) 
#SBATCH -c 1                   # CPUs por tarea (1; mpi puro)
#SBATCH -t 00:10:00            # Time limit (hh:mm:ss)

### ==== Ajusta tu entorno Python/MPI ====
cd /home/jfiestas/HPC/2025-II/U4.1-Distributed/PI/ 
module swap openmpi4 mpich/3.4.3-ofi 
module load py3-mpi4py                 

### ==== Parámetros de la corrida ====
N_STEPS=1048576          # total de intervalos 67108864, 33554432, 16777216, 4194304, 1048576 
SCRIPT=pi_mpi.py

### ==== Buenas prácticas de runtime ====
export OMP_NUM_THREADS=1       # Evita oversubscription (MPI puro)
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

### ==== Preparar carpeta de logs ====
mkdir -p logs_py

echo "==== INFO JOB ===="
echo "JobID: $SLURM_JOB_ID | JobName: $SLURM_JOB_NAME"
echo "Nodes: $SLURM_JOB_NUM_NODES | Tasks: $SLURM_NTASKS | TimeLimit: $SLURM_TIMELIMIT"
echo "Partition: $SLURM_JOB_PARTITION"
echo "Hostlist:"
scontrol show hostnames $SLURM_JOB_NODELIST

echo "==== Ejecutando ===="
mpirun --bind-to core --map-by core -np $SLURM_NTASKS python3.6 $SCRIPT -n $N_STEPS

