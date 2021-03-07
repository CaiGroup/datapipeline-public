#!/bin/bash

#Submit this script with:sbatch thefilename

#SBATCH --time=1:00:00   # walltime
#SBATCH --ntasks=20  # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
#SBATCH --mem-per-cpu=1G   # memory per CPU core
#SBATCH -J "test_adcg_fit"   # job name


# LOAD MODULES, INSERT CODE, AND RUN YOUR PROGRAMS HERE

module load julia/1.5.2

julia dot_detection/dot_detectors_3d/adcg/get_adcg_dots_v2.jl $1 $2
