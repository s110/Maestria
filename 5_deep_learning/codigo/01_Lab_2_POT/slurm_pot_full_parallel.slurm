#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# POT Full Training — 2 GPUs en paralelo (un dataset por GPU)
# ═══════════════════════════════════════════════════════════════════════════
# Lanza 2 jobs simultaneos:
#   GPU 0: COCO (el mas largo, ~3-4h)
#   GPU 1: Cityscapes + Mapillary (~50 min total)
#
# Uso:
#   bash slurm_pot_full_parallel.slurm
# ═══════════════════════════════════════════════════════════════════════════

echo "Lanzando 2 jobs en paralelo..."

# Job 1: COCO (lento, GPU propia)
JOB1=$(sbatch --parsable <<'SLURM1'
#!/bin/bash
#SBATCH --job-name=pot_coco
#SBATCH --output=logs/full_coco_%j.log
#SBATCH --error=logs/full_coco_err_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --nodelist=ag001
#SBATCH --gres=gpu:1

module purge
module load gnu12/12.4.0
module load python3/3.13.2
module load cuda/12.6
cd /home/sebastian.lopez/DL/01_lab_2_POT/ || exit
source .venv/bin/activate
mkdir -p logs results/full_training
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

echo "=== COCO Full Training === GPU: $CUDA_VISIBLE_DEVICES === $(date) ==="
nvidia-smi

srun python3 -u pot_full_training.py \
    --base-dir . \
    --output-dir ./results/full_training \
    --datasets coco \
    --img-size 448 \
    --batch-size 16 \
    --epochs 6 \
    --num-workers 8

echo "=== COCO done === $(date) ==="
SLURM1
)

# Job 2: Cityscapes + Mapillary (rapidos, comparten GPU)
JOB2=$(sbatch --parsable <<'SLURM2'
#!/bin/bash
#SBATCH --job-name=pot_city_map
#SBATCH --output=logs/full_city_map_%j.log
#SBATCH --error=logs/full_city_map_err_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --partition=gpu
#SBATCH --nodelist=ag001
#SBATCH --gres=gpu:1

module purge
module load gnu12/12.4.0
module load python3/3.13.2
module load cuda/12.6
cd /home/sebastian.lopez/DL/01_lab_2_POT/ || exit
source .venv/bin/activate
mkdir -p logs results/full_training
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

echo "=== Cityscapes + Mapillary Full Training === GPU: $CUDA_VISIBLE_DEVICES === $(date) ==="
nvidia-smi

srun python3 -u pot_full_training.py \
    --base-dir . \
    --output-dir ./results/full_training \
    --datasets cityscapes mapillary_vistas_v2 \
    --img-size 448 \
    --batch-size 16 \
    --epochs 6 \
    --num-workers 8

echo "=== Cityscapes + Mapillary done === $(date) ==="
SLURM2
)

echo "Job COCO:                $JOB1"
echo "Job Cityscapes+Mapillary: $JOB2"
echo ""
echo "Monitorear con:"
echo "  tail -f logs/full_coco_${JOB1}.log"
echo "  tail -f logs/full_city_map_${JOB2}.log"
