#!/bin/bash
#SBATCH --job-name=pot_full
#SBATCH --output=logs/full_training_%j.log
#SBATCH --error=logs/full_training_err_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=64G
#SBATCH --time=10:00:00
#SBATCH --partition=gpu
#SBATCH --nodelist=ag001
#SBATCH --gres=gpu:1

# ═══════════════════════════════════════════════════════════════════════════
# POT Full Training — Paper parameters, all datasets sequential
# ═══════════════════════════════════════════════════════════════════════════
# Estimacion de tiempo (A100, batch_size=16, img_size=448, GPU KMeans):
#   COCO:       118K imgs × 6 epochs ≈ 3-4 horas
#   Cityscapes:   3K imgs × 6 epochs ≈ 8 min
#   Mapillary:   18K imgs × 6 epochs ≈ 40 min
#   Total estimado: ~5 horas (+ evaluacion ~1h)
# ═══════════════════════════════════════════════════════════════════════════

echo "========================================================"
echo "POT Full Training — All Datasets Sequential"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodo: $(hostname)"
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
mkdir -p logs
mkdir -p results/full_training

# 5. Diagnostico GPU
echo "--- GPU ---"
nvidia-smi
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
python3 -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
echo "-----------"

# 6. Evitar contention de hilos
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

# 7. Ejecutar entrenamiento secuencial (COCO → Cityscapes → Mapillary)
echo "Iniciando entrenamiento secuencial..."
srun python3 -u pot_full_training.py \
    --base-dir . \
    --output-dir ./results/full_training \
    --datasets coco cityscapes mapillary_vistas_v2 \
    --img-size 448 \
    --batch-size 16 \
    --epochs 6 \
    --num-workers 8

echo "========================================================"
echo "Fin: $(date)"
echo "========================================================"
