#!/bin/bash
#SBATCH -A m4474_g
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --ntasks=1                   
#SBATCH --gpus-per-task=1
#SBATCH --time 6:00:00
#SBATCH --output log/%j.log
#SBATCH --job-name vqvae200

### go to the right directory relative to this script's location
PROJECT_ROOT="/global/cfs/cdirs/m3246/mpettee/hep/particlemind"

cd $PROJECT_ROOT

uv run python $PROJECT_ROOT/src/particlemind/training/train_vqvae.py --train_embedder --normalize --max_epochs 200