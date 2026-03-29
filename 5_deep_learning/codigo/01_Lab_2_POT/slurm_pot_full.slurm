#!/bin/bash
#SBATCH --job-name=pot_full
#SBATCH --output=logs/full_training_%j.log
#SBATCH --error=logs/full_training_err_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64G
#SBATCH --time=10:00:00
#SBATCH --partition=gpu
#SBATCH --nodelist=ag001
#SBATCH --gres=gpu:2

# ═══════════════════════════════════════════════════════════════════════════
# POT Full Training — 2 GPUs en paralelo dentro de 1 job
# ═══════════════════════════════════════════════════════════════════════════
#   GPU 0: COCO              (~3-4h)
#   GPU 1: Cityscapes + Mapillary (~50 min)
#   Tiempo total: el del mas lento (COCO)
# ═══════════════════════════════════════════════════════════════════════════

echo "========================================================"
echo "POT Full Training — 2 GPUs paralelas"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodo: $(hostname)"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Inicio: $(date)"
echo "========================================================"

# 1. Cargar modulos
module purge
module load gnu12/12.4.0
module load python3/3.13.2
module load cuda/12.6

# 2. Directorio de trabajo
cd /home/sebastian.lopez/DL/01_lab_2_POT/ || exit

# 3. Entorno virtual
source .venv/bin/activate

# 4. Directorios de salida
mkdir -p logs results/full_training

# 5. Diagnostico
echo "--- GPUs asignadas ---"
nvidia-smi -L
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
python3 -c "import torch; print(f'PyTorch {torch.__version__}, GPUs: {torch.cuda.device_count()}')"
echo "----------------------"

# 6. Evitar contention de hilos por proceso
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# ═══════════════════════════════════════════════════════════════════════════
# Lanzar 2 procesos en paralelo, cada uno con su GPU
# ═══════════════════════════════════════════════════════════════════════════

# GPU 0: COCO (el dataset mas grande)
echo "[$(date)] Lanzando COCO en GPU 0..."
CUDA_VISIBLE_DEVICES=0 python3 -u pot_full_training.py \
    --base-dir . \
    --output-dir ./results/full_training \
    --datasets coco \
    --img-size 448 \
    --batch-size 16 \
    --epochs 6 \
    --num-workers 8 \
    > logs/full_coco_${SLURM_JOB_ID}.log 2>&1 &
PID_COCO=$!

# GPU 1: Cityscapes + Mapillary (datasets mas rapidos)
echo "[$(date)] Lanzando Cityscapes + Mapillary en GPU 1..."
CUDA_VISIBLE_DEVICES=1 python3 -u pot_full_training.py \
    --base-dir . \
    --output-dir ./results/full_training \
    --datasets cityscapes mapillary_vistas_v2 \
    --img-size 448 \
    --batch-size 16 \
    --epochs 6 \
    --num-workers 8 \
    > logs/full_city_map_${SLURM_JOB_ID}.log 2>&1 &
PID_CITY_MAP=$!

echo ""
echo "PIDs: COCO=$PID_COCO | Cityscapes+Mapillary=$PID_CITY_MAP"
echo "Logs:"
echo "  tail -f logs/full_coco_${SLURM_JOB_ID}.log"
echo "  tail -f logs/full_city_map_${SLURM_JOB_ID}.log"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# Esperar a que ambos terminen
# ═══════════════════════════════════════════════════════════════════════════

wait $PID_CITY_MAP
EXIT_CM=$?
echo "[$(date)] Cityscapes+Mapillary terminado (exit code: $EXIT_CM)"

wait $PID_COCO
EXIT_COCO=$?
echo "[$(date)] COCO terminado (exit code: $EXIT_COCO)"

# ═══════════════════════════════════════════════════════════════════════════
# Resumen
# ═══════════════════════════════════════════════════════════════════════════
echo ""
echo "========================================================"
echo "Ambos procesos terminados"
echo "  COCO:                exit=$EXIT_COCO"
echo "  Cityscapes+Mapillary: exit=$EXIT_CM"
echo "  Resultados en: ./results/full_training/"
echo "Fin: $(date)"
echo "========================================================"
