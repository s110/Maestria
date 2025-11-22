#!/bin/bash

#SBATCH --job-name=fer2013_training  # Name of your job
#SBATCH --output=logs/slurm_output_%j.log # Log file for stdout/stderr, %j will be replaced by the job ID
#SBATCH --nodes=1                    # Request one node
#SBATCH --ntasks-per-node=1          # Run one task (your python script) on that node
#SBATCH --cpus-per-task=4            # Request 4 CPUs. Good for data loaders (`num_workers=4`)
#SBATCH --time=02:00:00              # Set a time limit of 1 hour for the job
#SBATCH --partition=data-science
#SBATCH --nodelist=ds001             # Request ds001 for internet access
# --- Your setup and commands go below this line ---

echo "========================================================"
echo "Starting job $SLURM_JOB_ID at $(date)"
echo "========================================================"

# 1. Load necessary modules (IMPORTANT: Adjust for your cluster)
#    Use `module avail` on your cluster to see available modules.
echo "Loading modules..."
module purge
module load gnu12/12.4.0  # GNU compiler, often a dependency
module load python3/3.13.2
module load cuda/11.8

# 2. Activate your Python virtual environment
#    This command assumes your script is run from the project root.
echo "Activating Python environment..."
cd ~/CV/01_laboratorio_3/
source .venv/bin/activate

# 4. Run your Python script
echo "Executing Python script..."
python -u tarea_3_cv_script.py
# The "-u" flag ensures that Python's output is unbuffered and prints to the log file in real-time.
