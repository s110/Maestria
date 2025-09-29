#!/bin/bash
#SBATCH --job-name=rf-grid
#SBATCH --partition=standard
#SBATCH --output=logs/rf_%x_%A_%a.out
#SBATCH --error=logs/rf_%x_%A_%a.err
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
# total de combinaciones = (#N_JOBS) * (#SIZES)
# aquí: N_JOBS_OPTS=(4 8 16 32)  => 4 valores
#       SIZES=(100k 200k 400k 800k) => 4 valores
# 4 * 4 = 16 combinaciones, indices 0..15
#SBATCH --array=0-15

mkdir -p logs

# (activa tu env si aplica)
# module load python/3.10
# source ~/venvs/py310/bin/activate
cd ~/HPC/semana_4/random_forest/run_01

# Evitar sobresuscripción BLAS
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Grillas
N_JOBS_OPTS=(4 8 16 32)
SIZES=(100000 200000 400000 800000)

# Mapeo 2D
NUM_J=${#N_JOBS_OPTS[@]}
NUM_S=${#SIZES[@]}
IDX=${SLURM_ARRAY_TASK_ID}

J_IDX=$(( IDX % NUM_J ))
S_IDX=$(( IDX / NUM_J ))

N_JOBS=${N_JOBS_OPTS[$J_IDX]}
N_SAMPLES=${SIZES[$S_IDX]}

# Exporta hilos para el script
export N_JOBS="${N_JOBS}"

echo "[INFO] Combo: N_JOBS=${N_JOBS}  N_SAMPLES=${N_SAMPLES}"

srun python3 rf.py \
  --n_samples ${N_SAMPLES} \
  --n_features 40 \
  --n_informative 20 \
  --n_redundant 10 \
  --n_classes 2 \
  --n_estimators 400 \
  --max_depth 20 \
  --test_size 0.2 \
  --reps 3 \
  --output results_rf_synth.csv

