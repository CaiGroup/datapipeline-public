#Activate conda environment to get correct packages
PYTHON_BIN_PATH=/groups/CaiLab/personal/python_env/bin
source ${PYTHON_BIN_PATH}/activate_batch

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <datapipeline source directory> <JSON directory>"
  exit 127
fi

DATA_PIPELINE_DIR=$1

cd $DATA_PIPELINE_DIR

#Runs script for checking for jsons in source directory
#----------------------------------------------
${PYTHON_BIN_PATH}/python ${DATA_PIPELINE_DIR}/check_for_jsons.py --source_of_jsons ${2}
