#!/bin/bash
#SBATCH --job-name=heat-mpi
#SBATCH --output=logs/heat_%x_%A_%a.out
#SBATCH --error=logs/heat_%x_%A_%a.err
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclusive
# --- CONFIGURACIÓN DEL ARRAY ---
# Vamos a probar:
# Procesos (P): 1, 2, 4, 8, 16, 32 (6 variantes)
# Tamaños (N):  200, 800, 1600, 3200 (4 variantes)
# Total combinaciones: 6 * 4 = 24
#SBATCH --array=0-23

# Cargar módulos (AJUSTA ESTO SEGÚN TU CLUSTER)
# module load openmpi/4.1.4  <-- Ejemplo, descomenta si es necesario

mkdir -p logs

# --- DEFINICIÓN DE VARIABLES ---
# Lista de procesos a probar (P)
PROCS_OPTS=(1 2 4 8 16 32)
# Lista de tamaños de matriz a probar (N)
SIZES_OPTS=(200 800 1600 3200)

# --- MAPEO DEL INDICE (Igual que tu ejemplo de Python) ---
NUM_P=${#PROCS_OPTS[@]}
NUM_S=${#SIZES_OPTS[@]}
IDX=${SLURM_ARRAY_TASK_ID}

# Matemáticas para sacar la combinación
P_IDX=$(( IDX % NUM_P ))
S_IDX=$(( IDX / NUM_P ))

N_PROCS=${PROCS_OPTS[$P_IDX]}
MATRIX_SIZE=${SIZES_OPTS[$S_IDX]}

echo "=========================================="
echo "Ejecutando Heat Equation MPI"
echo "Job ID: ${SLURM_JOB_ID} - Array ID: ${SLURM_ARRAY_TASK_ID}"
echo "Configuración: Procesos=$N_PROCS, Tamaño=${MATRIX_SIZE}x${MATRIX_SIZE}"
echo "=========================================="

# --- EJECUCIÓN ---
# Sintaxis: mpirun -np [NumProcesos] ./[Ejecutable] [ArgumentoTamaño]
mpirun -np $N_PROCS ./heat_mpi $MATRIX_SIZE

echo "Finalizado."