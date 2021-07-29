#!/bin/bash

# Install script to set up the proper environment for running the data pipeline
# under a new user account.

cd

mkdir -p test_analyses
mkdir -p json_analyses
mkdir -p /central/scratch/$USER

ACTCMD="source /groups/CaiLab/personal/python_env/bin/activate"
echo "Make sure to activate the environment with:"
echo
echo $ACTCMD
echo
echo "before running the pipeline."


