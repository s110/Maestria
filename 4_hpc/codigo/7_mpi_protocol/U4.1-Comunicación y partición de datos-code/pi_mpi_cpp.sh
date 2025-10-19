#!/bin/bash
#SBATCH -J pi-mpi-cpp             # Nombre del job
#SBATCH -o logs_c/%x.%j.out         # Stdout
#SBATCH -e logs_c/%x.%j.err         # Stderr
#SBATCH -p standard               # partición
#SBATCH -N 1                      # Nodos
#SBATCH -n 16                      # Tareas MPI (procesos)
#SBATCH -c 1                      # CPUs por tarea
#SBATCH -t 00:10:00               # Límite de tiempo

# ====== VARIABLES ======
SRC=pi_mpi.cpp            # fuente C++
EXE=pi_mpi_cpp
N_STEPS=67108864 	# total de intervalos 67108864, 33554432, 16777216, 4194304, 1048576 
cd /home/jfiestas/HPC/2025-II/U4.1-Distributed/PI

# Buenas prácticas: MPI puro (evita oversubscription de librerías BLAS/OpenMP)
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# ====== PREP ======
mkdir -p logs_c

echo "==== INFO JOB ===="
echo "JobID=$SLURM_JOB_ID Name=$SLURM_JOB_NAME"
echo "Nodes=$SLURM_JOB_NUM_NODES Tasks=$SLURM_NTASKS CPUs/Task=$SLURM_CPUS_PER_TASK"
echo "Partition=$SLURM_JOB_PARTITION TimeLimit=$SLURM_TIMELIMIT"
echo "Hostlist:"; scontrol show hostnames $SLURM_JOB_NODELIST

# ====== EJECUCION ======
echo "== Ejecutando =="
echo "srun -n $SLURM_NTASKS build/${EXE} $N_STEPS"
mpirun -n $SLURM_NTASKS ${EXE} $N_STEPS

