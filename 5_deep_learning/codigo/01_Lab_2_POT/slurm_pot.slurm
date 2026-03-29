#!/bin/bash
#SBATCH --job-name=pot_train
#SBATCH --output=logs/results_%j.log
#SBATCH --error=logs/error_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --nodelist=ag001
#SBATCH --gres=gpu:2

# ═══════════════════════════════════════════════════════════════════════════
# POT: Prototypical Optimal Transport — SLURM Batch Script
# ═══════════════════════════════════════════════════════════════════════════
# Uso:
#   sbatch slurm_pot.slurm cityscapes
#   sbatch slurm_pot.slurm coco
# ═══════════════════════════════════════════════════════════════════════════

# Validar argumento de dataset
DATASET=${1:-cityscapes}
if [[ "$DATASET" != "cityscapes" && "$DATASET" != "coco" && "$DATASET" != "mapillary_vistas_v2" ]]; then
    echo "ERROR: Dataset debe ser 'cityscapes' o 'coco'. Recibido: $DATASET"
    exit 1
fi

echo "========================================================"
echo "POT Training — Dataset: $DATASET"
echo "Job ID: $SLURM_JOB_ID"
echo "Nodo: $(hostname)"
echo "Inicio: $(date)"
echo "========================================================"

# 1. Cargar módulos
echo "Cargando módulos..."
module purge
module load gnu12/12.4.0
module load python3/3.13.2
module load cuda/12.6

# 2. Directorio de trabajo
cd /home/sebastian.lopez/DL/01_lab_2_POT/ || exit

# 3. Activar entorno virtual
echo "Activando entorno virtual..."
source .venv/bin/activate

# 4. Crear directorios de salida
mkdir -p logs
mkdir -p results/$DATASET

# 5. Verificar GPU
#echo "Verificando GPU..."
#python3 -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'No GPU')"
# 5. Verificar GPU (Diagnóstico completo)
echo "--- DIAGNÓSTICO DE GPU ---"
echo "1. Ejecutando nvidia-smi (¿SLURM nos dio la GPU?):"
nvidia-smi

echo "2. Variable CUDA_VISIBLE_DEVICES:"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

echo "3. Versión de PyTorch:"
python3 -c "import torch; print(f'Versión: {torch.__version__}')"

echo "4. Test de CUDA en PyTorch:"
python3 -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}')"
echo "--------------------------"


# 6. Ejecutar entrenamiento
echo "Ejecutando script POT con dataset: $DATASET"
srun python3 -u pot_cityscapes_colab.py \
    --dataset $DATASET \
    --base-dir . \
    --output-dir ./results \
    --epochs 6 \
    --batch-size 4 \
    --num-workers 8

echo "========================================================"
echo "Fin: $(date)"
echo "========================================================"
