#!/bin/bash
# --- Directivas SBATCH (TODAS AL PRINCIPIO) ---
#SBATCH --job-name=rnn_joblib_ex5
#SBATCH --partition=standard
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --output=logs_ex5/rnn_%x_%A_%a.out
#SBATCH --error=logs_ex5/rnn_%x_%A_%a.err
#SBATCH --array=0-35

# --- CONFIGURACIÓN DEL GRID SEARCH ---
N_FEATURES_VALUES=(64 128 256)
JOBS_VALUES=(1 2 4 8 16 32)
N_SAMPLES_VALUES=(10000)
HIDDEN_LAYER_CONFIGS=(
    "256;256,128;512,256,128"
    "64;128;128,64"
)

NUM_F=${#N_FEATURES_VALUES[@]}
NUM_J=${#JOBS_VALUES[@]}
NUM_S=${#N_SAMPLES_VALUES[@]}
NUM_HLS=${#HIDDEN_LAYER_CONFIGS[@]}
TOTAL_COMBOS=$(( NUM_J * NUM_S * NUM_F * NUM_HLS ))
ARRAY_MAX_IDX=$(( TOTAL_COMBOS - 1 ))

# --- Directivas SBATCH Dependientes ---
# NOTA: Las rutas de output/error son relativas al directorio de trabajo final.
# Nos aseguraremos de que ese directorio exista antes de que SLURM lo necesite.
# --- Preparación del Entorno de Ejecución ---
# (Opcional) Módulos y entorno virtual
# module load python/3.10
#
# Modificacion

# --- CORRECCIÓN 2: Construir la ruta al script de forma robusta ---
# Asumiendo que `rnn_joblib.py` está en el mismo directorio que este script de SLURM.
# Si está en una subcarpeta, ajústalo (ej. `${SLURM_SUBMIT_DIR}/scripts/rnn_joblib.py`)
PYTHON_SCRIPT_PATH="${SLURM_SUBMIT_DIR}/rnn_joblib_ex5.py"

# Crea un directorio único para este experimento y entra en él
# El `cd` se hace relativo al directorio desde donde se lanzó sbatch.
cd "${SLURM_SUBMIT_DIR}"
TIMESTAMP=$(date +'%Y%m%d')
EXPERIMENT_DIR="run_ex5_${TIMESTAMP}"
mkdir -p "${EXPERIMENT_DIR}" && cd "${EXPERIMENT_DIR}"

# --- CORRECCIÓN 1: Crear el directorio para los logs ---
# Esto es CRÍTICO. Debe existir antes de que SLURM intente escribir en él.
mkdir -p logs_ex5

# --- Evitar oversubscription BLAS ---
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# --- Mapeo del índice del array a los parámetros ---
IDX=${SLURM_ARRAY_TASK_ID}
HLS_IDX=$(( (IDX / (NUM_J * NUM_S * NUM_F)) % NUM_HLS ))
F_IDX=$(( (IDX / (NUM_J * NUM_S)) % NUM_F ))
J_IDX=$(( IDX % NUM_J ))
S_IDX=$(( (IDX / NUM_J) % NUM_S ))

N_FEATURES=${N_FEATURES_VALUES[$F_IDX]}
N_JOBS=${JOBS_VALUES[$J_IDX]}
N_SAMPLES=${N_SAMPLES_VALUES[$S_IDX]}
HLS_CONFIG=${HIDDEN_LAYER_CONFIGS[$HLS_IDX]}


OUTPUT_PREFIX="results_hls${HLS_IDX}_f${N_FEATURES}_j${N_JOBS}_s${N_SAMPLES}"
MODEL_FILE="${OUTPUT_PREFIX}_model.joblib"
METRICS_FILE="${OUTPUT_PREFIX}_metrics.csv"

# --- Mensajes informativos para el log ---
echo "[INFO] Tarea ${IDX}: HLS_CONFIG=${HLS_CONFIG}, N_FEATURES=${N_FEATURES}, N_JOBS=${N_JOBS}, N_SAMPLES=${N_SAMPLES}"
echo "[INFO] Directorio de trabajo: $(pwd)"
echo "[INFO] Ejecutando script: ${PYTHON_SCRIPT_PATH}"
echo "[INFO] Archivo de modelo: ${MODEL_FILE}"
echo "[INFO] Archivo de métricas: ${METRICS_FILE}"

# --- Comando `srun` modificado ---
srun python3 "${PYTHON_SCRIPT_PATH}" train \
  --n-samples "${N_SAMPLES}" --n-features "${N_FEATURES}" --classes 4 \
  --seeds 16 --max-iter 200 \
  --n-jobs "${N_JOBS}" --backend loky --inner-n-jobs 1 \
  --out-model "${MODEL_FILE}" \
  --metrics-csv "${METRICS_FILE}" \
  --hidden-layer-sizes "${HLS_CONFIG}"
