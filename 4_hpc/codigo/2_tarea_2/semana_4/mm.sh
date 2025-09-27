#!/bin/bash
#SBATCH --job-name=mm
#SBATCH --output=mm_%x_%A_%a.log
#SBATCH --error=error_%A_%a.log
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --array=1,2,4,8,16,32

cd /home/sebastian.lopez/HPC/semana_4

# === Hilos a usar en este sub-job (desde el índice del array) ===
NTHREADS="${SLURM_ARRAY_TASK_ID}"

# No exceder lo asignado por Slurm
if [[ -n "$SLURM_CPUS_PER_TASK" && "$NTHREADS" -gt "$SLURM_CPUS_PER_TASK" ]]; then
  echo "Ajustando NTHREADS=$NTHREADS -> $SLURM_CPUS_PER_TASK"
  NTHREADS="$SLURM_CPUS_PER_TASK"
fi

# === Variables de entorno OpenMP recomendadas ===
export OMP_NUM_THREADS="${NTHREADS}"
export OMP_PROC_BIND=close         # fija hilos pegados al proceso
export OMP_PLACES=cores            # una hebra por core físico
export OMP_DYNAMIC=false           # no autorregular hilos

# Si tu binario acepta hilos por argv, pásalos también (doble cinturón):
#   ./mm_openmp <N> <threads>
N=16384

echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}"
echo "Ejecutando con OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "OMP_PROC_BIND=${OMP_PROC_BIND}  OMP_PLACES=${OMP_PLACES}"

# Para evitar SMT si tu cluster lo recomienda:
#   añade --hint=nomultithread (opcional, depende del site)
srun --cpu-bind=cores ./mm_openmp 4096 "${NTHREADS}"

