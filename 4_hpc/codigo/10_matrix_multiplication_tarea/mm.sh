#!/bin/bash
#SBATCH --job-name=mm
#SBATCH --output=mm_%x_%A_%a.log     # %A = jobID del array, %a = índice del array
#SBATCH --error=error_%A_%a.log
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16           # pide el MAXIMO de hilos que probarás
#SBATCH --array=1,2,4,8,16           # valores de hilos a barrer

# ===== Directorio y módulos =====
cd /home/jfiestas/2025-II/U2.2-MM-numpy-OMP/run03
#ml load python3

# ===== Determinar NTHREADS de este sub-job =====
NTHREADS="${SLURM_ARRAY_TASK_ID}"

# Seguridad: no exceder lo que nos dio SLURM (-c)
if [[ -n "$SLURM_CPUS_PER_TASK" && "$NTHREADS" -gt "$SLURM_CPUS_PER_TASK" ]]; then
  echo "Ajustando NTHREADS=$NTHREADS -> $SLURM_CPUS_PER_TASK (límite cpus-per-task)"
  NTHREADS="$SLURM_CPUS_PER_TASK"
fi

echo "Ejecutando con NTHREADS=${NTHREADS} (cpus-per-task=${SLURM_CPUS_PER_TASK})"

# ===== Ejecutar =====
# srun respeta el binding y el -c solicitado
#srun --cpu-bind=cores python3 mm_numpy.py
	srun --cpu-bind=cores ./mm_openmp
