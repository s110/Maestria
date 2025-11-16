#!/bin/bash
#SBATCH --job-name=matmul_grid
#SBATCH --partition=standard             # O 'debug' para pruebas cortas
#SBATCH --output=logs/matmul_%A_%a.out   # Salida: %A=JobID, %a=TaskID
#SBATCH --error=logs/matmul_%A_%a.err
#SBATCH --time=01:00:00                  # Tiempo máximo (ajustar según necesidad)
#SBATCH --nodes=1
#SBATCH --array=0-47
#SBATCH --ntasks-per-node=32 # Solicitamos el máximo de la lista
#SBATCH --cpus-per-task=1

# --- Definición de la Grilla de Parámetros ---
NTASKS_OPTS=(1 2 4 8 16 32)
MATRIX_SIZES_OPTS=(1024 2048 4096 8192 16384 32768 65536 131072)

# --- Cálculo del Tamaño del Array Job ---
# Total de combinaciones = (#NTASKS_OPTS) * (#MATRIX_SIZES_OPTS)
NUM_NTASKS=${#NTASKS_OPTS[@]}
NUM_SIZES=${#MATRIX_SIZES_OPTS[@]}
TOTAL_COMBOS=$((NUM_NTASKS * NUM_SIZES))
MAX_INDEX=$((TOTAL_COMBOS - 1))

# --- Configuración del Array Job ---


# --- Mapeo del Task ID a los Parámetros ---
# El SLURM_ARRAY_TASK_ID irá de 0 a MAX_INDEX
IDX=${SLURM_ARRAY_TASK_ID}

# Mapeo 2D: Usamos módulo y división para obtener los índices
NTASKS_IDX=$(( IDX % NUM_NTASKS ))
SIZE_IDX=$(( IDX / NUM_NTASKS ))

# Seleccionamos los parámetros para esta tarea específica del array
CURRENT_NTASKS=${NTASKS_OPTS[$NTASKS_IDX]}
CURRENT_SIZE=${MATRIX_SIZES_OPTS[$SIZE_IDX]}

# --- Configuración de SLURM Dinámica ---
# Sobrescribimos el número de tareas para este job específico
# (Esto requiere que el script sea lanzado con ntasks=1 y luego lo ajustamos)
# NOTA: La directiva #SBATCH --ntasks no se puede cambiar dinámicamente.
# En su lugar, pasamos el número de procesos directamente a mpiexec.
# Para que SLURM asigne los recursos correctos, debemos solicitar el MÁXIMO
# de cpus/tareas que necesitaremos en todo el array.

# --- Configuración del Entorno ---
echo "======================================================"
echo "Job ID: $SLURM_JOB_ID, Task ID: $SLURM_ARRAY_TASK_ID"
echo "Mapeo: NTASKS=${CURRENT_NTASKS}, MATRIX_SIZE=${CURRENT_SIZE}"
echo "Ejecutando en los nodos: $SLURM_JOB_NODELIST"
echo "======================================================"

module load python3

# Crear y activar entorno virtual
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

module swap openmpi4 mpich/3.4.3-ofi


# --- Ejecución del Programa ---
echo "Iniciando ejecución..."

# mpiexec usará el número de procesos que le pasemos,
# siempre que no exceda los recursos que SLURM nos ha asignado.
mpiexec -n ${CURRENT_NTASKS} python3 matmul_mpi_torch.py --size ${CURRENT_SIZE} --verify

echo "Ejecución finalizada."
