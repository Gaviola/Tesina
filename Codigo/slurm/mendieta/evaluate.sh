#!/bin/bash
#SBATCH --job-name=dermvlm_eval
#SBATCH --output=/home/%u/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/shared/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus-per-task=1
#SBATCH --time=1-00:00:00

. /etc/profile
source activate dermvlm

# Nodos de computo no tienen internet — usar modelos pre-descargados del cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

nvidia-smi

# Evaluación Nivel 1: Métricas automáticas con referencia
python scripts/evaluate_reports.py --model llava_med --level 1
python scripts/evaluate_reports.py --model mini_vlm --level 1

# Evaluación Nivel 2: Entidades clínicas (NER)
python scripts/evaluate_reports.py --model llava_med --level 2
python scripts/evaluate_reports.py --model mini_vlm --level 2
