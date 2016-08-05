#!/bin/bash

# Request an hour of runtime:
#SBATCH --time=1:00:00

# Default resources are 1 core with 2.8GB of memory.

# Use more memory (4GB):
#SBATCH --mem=8G

# Use more cores
#SBATCH -n 4

# Specify a job name:
#SBATCH -J TestPythonScript

# Specify an output file
#SBATCH -o test-%j.out
#SBATCH -e test-%j.out

# Run a matlab script called 'foo.m' in the same directory as this batch script.
source venv1/bin/activate
python freq_noise.py data/psa128
