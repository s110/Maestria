#!/bin/bash
#SBATCH --job-name=knn-grid-search
#SBATCH --output=logs/knn_grid_search_%j.log
#SBATCH --error=logs/error_grid_search_%j.log
#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --partition=standard

# Cargar modulos si es necesario

mkdir -p logs
ml load python3
source venv/bin/activate
module swap openmpi4 mpich/3.4.3-ofi
module load py3-mpi4py
module load py3-numpy
module load py3-scipy

TRAIN_SIZES=(100000 640000 1000000)
NTASKS=(1 2 4 8 16 32)

echo "Starting grid search for knn_mpi.py" >&2
echo "Train sizes: ${TRAIN_SIZES[@]}" >&2
echo "N_tasks: ${NTASKS[@]}" >&2

# Clean previous results if any
[ -f knn_mpi_results.csv ] && rm knn_mpi_results.csv

for ntasks in "${NTASKS[@]}"; do
  if [ "$ntasks" -gt "$SLURM_NTASKS" ]; then
    echo "Skipping ntasks=$ntasks, as it is greater than allocated tasks ($SLURM_NTASKS)." >&2
    continue
  fi
  for train_size in "${TRAIN_SIZES[@]}"; do
    echo "----------------------------------------" >&2
    echo "Running with ntasks=$ntasks and train_size=$train_size" >&2
    mpiexec -n "$ntasks" python3.6 knn_mpi.py "$train_size"
    echo "----------------------------------------" >&2
  done
done

echo "Grid search finished." >&2
echo "Results saved in knn_mpi_results.csv" >&2

module unload openmpi4 mpich/3.4.4-ofi
module unload py3-mpi4py
module unload py3-numpy
module unload py3-scipy
