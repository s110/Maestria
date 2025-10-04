#!/bin/bash
#SBATCH --job-name=knn_joblib
#SBATCH --output=knn_out_%j.txt
#SBATCH --error=knn_err_%j.txt
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:20:00
#SBATCH --partition=standard

echo "Inicio del experimento: $(date)"
echo "Corriendo con ${SLURM_CPUS_PER_TASK} hilos..."

# Ejecuta el script Python, que genera automáticamente el CSV
python3 knn_digits_joblib_scale.py \
    --k 5 \
    --jobs ${SLURM_CPUS_PER_TASK} \
    --mult-train 160 \
    --mult-test 2 \
    --feat-mult 2 \
    --backend threading \
    --jitter 0.1

#echo "Fin del experimento: $(date)"

# Renombrar el CSV para que no se sobreescriba si corres muchos jobs en paralelo
#CSV_FILE="knn_scalability_results.csv"
#RENAMED_CSV="knn_results_${SLURM_JOB_ID}.csv"

#if [ -f "$CSV_FILE" ]; then
#    mv "$CSV_FILE" "$RENAMED_CSV"
#    echo "📁 CSV renombrado a $RENAMED_CSV"
#fi

