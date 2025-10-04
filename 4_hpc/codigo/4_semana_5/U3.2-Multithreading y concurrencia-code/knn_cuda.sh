#!/bin/bash
#SBATCH --job-name=knn_cuda
#SBATCH --output=knn_cuda_out_%j.txt
#SBATCH --error=knn_cuda_err_%j.txt
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --mem=8G

# reemplace aqui su ruta
cd /home/jfiestas/HPC/2025-II/U3.1-Multithreading_2/knn/GPU/cuda/

module load cuda || true

echo "Nodelist: $SLURM_NODELIST"
N=862080 
D=128
K=5
SEED=42

Q_LIST="512 1024 2048 4096 8192 16384"

for Q in $Q_LIST; do
  echo "[Run] N=$N Q=$Q D=$D K=$K"
    srun ./knn_cuda -N $N -Q $Q -D $D -k $K -seed $SEED 
done


