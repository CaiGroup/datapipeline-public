#!/bin/bash -l


#Load Matlab Module (This does not work on the cronjob:
#for the cronjob I manually alter the $PATH variable to load matlab)
#I put here because this is how you get matlab when debugging
#----------------------------------------------
module load matlab/r2019a
#----------------------------------------------



#Activate conda environment to get correct packages
#----------------------------------------------
source ~/miniconda3/etc/profile.d/conda.sh
conda activate data-pipeline
#----------------------------------------------


#Runs script that sets parameters and runs the analysis. It imports analysis_class.py to do so.
#----------------------------------------------
python ${6}/json_analysis.py --json ${1} --position ${2} --personal ${3} --experiment_name ${4} --slurm ${5} --email ${7}
#----------------------------------------------
