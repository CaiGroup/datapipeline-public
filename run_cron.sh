
#Activate conda environment to get correct packages
#----------------------------------------------
source /groups/CaiLab/personal/python_env/bin/activate
#conda activate data-pipeline
#----------------------------------------------


#I have to add this because when the cronjon runs it assumes you want $HOME/check_for_jsons.py
#----------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#----------------------------------------------


#Runs script for checking for jsons in source directory
#----------------------------------------------
python ${DIR}/check_for_jsons.py --source_of_jsons ${1}
#----------------------------------------------
