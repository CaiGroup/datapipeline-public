#!/bin/bash -l

#Load Matlab Module (This does not work on the cronjob:
#for the cronjob I manually alter the $PATH variable to load matlab)
#I put here because this is how you get matlab when debugging
#----------------------------------------------
module load matlab/r2019a
#----------------------------------------------



#Activate conda environment to get correct packages
#----------------------------------------------
source /groups/CaiLab/personal/python_env/bin/activate_batch
#conda activate data-pipeline
#----------------------------------------------

# Arguments fed to this script by check_for_jsons.py are:
# $1 - json_name (the analysis name plus .json)
# $2 - position name (full image name)
# $3 - personal (user)
# $4 - experiment_name
# $5 - running_in_slurm
# $6 - directory containing these scripts
# $7 - email address

json_name=${1%.json}
position_name=${2%%.*}
analysis_dir=/groups/CaiLab/analyses/$3/$4/$json_name/

python $6/check_experiment.py /groups/CaiLab/personal/$3/raw/$4 \
    --output $analysis_dir/experiment_check.txt

if [[ $? -ne 0 ]]; then
    chmod -R 770 $analysis_dir
    exit 1
fi

#Runs script that sets parameters and runs the analysis. It imports analysis_class.py to do so.
#----------------------------------------------
python ${6}/json_analysis.py --json ${1} --position ${2} --personal ${3} --experiment_name ${4} --slurm ${5} --email ${7}
#----------------------------------------------
if [[ $? -ne 0 ]]; then
    chmod -R 770 $analysis_dir
    exit 1
fi
