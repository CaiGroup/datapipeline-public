import glob
import os
import subprocess
import time

from .helpers.combine_offs import combine_align_errors
from .helpers.combine_offs import combine_offsets
# Import Multiprocessing helper
# -------------------------------------------------
from .helpers.rand_list import are_jobs_finished, get_random_list

# -------------------------------------------------

# Import DAPI Visual Check
# -------------------------------------------------

# -------------------------------------------------


main_dir = '/groups/CaiLab'


def get_and_sort_hybs(path_to_experiment_dir):
    """
    Gets and sorts the hybs
    """
    # Get all files in path
    # -------------------------------------------------
    hyb_dirs = glob.glob(path_to_experiment_dir)
    # -------------------------------------------------

    # Get background
    # -------------------------------------------------
    back_dir = [hyb_dir for hyb_dir in hyb_dirs if 'final_background' in hyb_dir]
    print(f'{back_dir=}')
    # -------------------------------------------------

    # Remove anything that is not a Hyb
    # -------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in hyb_dirs if 'HybCycle' in hyb_dir]
    # -------------------------------------------------

    # Split hybs to get numbers
    # -------------------------------------------------
    split_word = 'Cycle_'
    for index in range(len(hyb_dirs)):
        hyb_dirs[index] = hyb_dirs[index].split(split_word)

        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    # -------------------------------------------------

    # Sort the Hybs
    # -------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    # -------------------------------------------------

    # Combine the strings to right format
    # -------------------------------------------------
    for index in range(len(sorted_hyb_dirs)):
        sorted_hyb_dirs[index][1] = str(sorted_hyb_dirs[index][1])
        sorted_hyb_dirs[index].insert(1, split_word)
        sorted_hyb_dirs[index] = ''.join(sorted_hyb_dirs[index])
    # -------------------------------------------------

    # Add background to dirs to align
    # -------------------------------------------------
    if len(back_dir) == 1:
        sorted_hyb_dirs.append(back_dir[0])
    # -------------------------------------------------

    return sorted_hyb_dirs


def get_fixed_and_movings(exp_name, personal, position, main_dir):
    """
    Get fixed and moving images from details of experiment
    """
    # Get Fixed File Path and Sub Dirs
    # -------------------------------------------------
    exp_dir = os.path.join(main_dir, 'personal', personal, 'raw', exp_name)
    sub_dirs = get_and_sort_hybs(os.path.join(exp_dir, '*'))
    fixed_hyb = sub_dirs[0].split(os.sep)[-1]
    fixed_file_path = os.path.join(exp_dir, fixed_hyb, position)
    # -------------------------------------------------

    return sub_dirs, fixed_file_path


def run_alignment(exp_name, personal, position, align_function, num_wav, start_time):
    """
    Run alignmnet on a position and experiment
    """

    # Get Subdirectories and fixed file path
    # -------------------------------------------------
    sub_dirs, fixed_file_path = get_fixed_and_movings(exp_name, personal, position, main_dir)
    # -------------------------------------------------

    # Get random list for parallelization and where to store rand dirs
    # -------------------------------------------------
    rand_list = get_random_list(len(sub_dirs))
    temp_dir = os.path.join(main_dir, 'personal', 'temp', 'temp_align')
    # -------------------------------------------------

    # Get the directory with alignment scripts
    # -------------------------------------------------
    align_dir = os.path.dirname(__file__)
    # -------------------------------------------------

    # If no alignment set to "no_align"
    # -------------------------------------------------
    if align_function == 'no_align':
        offsets = {}
    # -------------------------------------------------

    # Run alignment
    # -----------------------------------------------------------------
    for sub_dir in sub_dirs:

        tiff_file_path = os.path.join(sub_dir, position)

        # Print Statement
        # -----------------------------------------------------------------
        hyb = sub_dir.split(os.sep)[-1]
        if align_function != 'no_align':
            print("    Running Alignment on", hyb, 'for', position, flush=True)
        # -----------------------------------------------------------------

        # Declare Random Dir
        # -----------------------------------------------------------------
        rand = rand_list[sub_dirs.index(sub_dir)]
        temp_dir = os.path.join(main_dir, 'personal', 'temp', 'temp_align')
        rand_dir = os.path.join(temp_dir, rand)
        try:
            os.mkdir(rand_dir)
        except FileExistsError:
            pass
        # -----------------------------------------------------------------

        # If there is no alignment
        # -------------------------------------------------
        if align_function == 'no_align':
            key = os.path.join(hyb, position)
            offsets[key] = [0, 0, 0]
        # -------------------------------------------------

        # Have to wait for dot detection to finish if there is fiducial alignment
        # -------------------------------------------------
        elif align_function == 'fiducial_markers':
            pass
            # -------------------------------------------------


        # Run DAPI Alignment
        # -------------------------------------------------
        else:
            print(f'{tiff_file_path=}')

            # Make Command and assign to bash script
            # -------------------------------------------------
            list_cmd = ['python', align_dir + '/' + align_function + '.py', '--fixed_src', fixed_file_path,
                        '--moving_src', tiff_file_path, '--rand', rand_dir, '--num_wav', str(num_wav)]
            cmd = ' '.join(list_cmd)
            # -------------------------------------------------

            # Write command to bash script to run in parallel
            # -------------------------------------------------
            script_name = os.path.join(rand_dir, 'align.sh')
            print(f'{script_name=}')
            out_file_path = os.path.join(rand_dir, 'slurm_align.out')
            with open(script_name, 'w') as f:
                f.write('#!/bin/bash \n')
                f.write(cmd)
            # -------------------------------------------------

            # Run Batch script command
            # -------------------------------------------------

            # Add extra resources for matlab 3d
            # -----------------
            if align_function == 'matlab_dapi':
                time_for_slurm = '01:00:00'
                ntasks = str(5)
                mem_per_cpu = '15G'
            else:
                time_for_slurm = '01:00:00'
                ntasks = str(1)
                mem_per_cpu = '10G'
            # -----------------
            print('-----------------------------------------------')
            print(f'{script_name=}')
            call_me = ['sbatch', '--output', out_file_path, '--job-name', rand_list[sub_dirs.index(sub_dir)], "--time",
                       time_for_slurm, "--mem-per-cpu", mem_per_cpu, "--ntasks", ntasks, script_name]
            print(f'{" ".join(call_me)=}')
            subprocess.call(call_me)
            # -------------------------------------------------

    # Only run if Align param is not no align
    # -------------------------------------------------
    if align_function != 'no_align':
        print(f'{rand_list=}')

        # Wait for all jobs to finish
        # -------------------------------------------------
        while not are_jobs_finished(rand_list):
            print('Waiting for Alignment Jobs to Finish')
            time.sleep(5)
        # -------------------------------------------------

        # Combine all offsets
        # -------------------------------------------------
        offsets = combine_offsets(rand_list)
        # -------------------------------------------------

        # Combine align errors
        # -------------------------------------------------
        align_errors = combine_align_errors(rand_list)
        # -------------------------------------------------

        # Delete Temp Directories
        # -------------------------------------------------
        # for rand in rand_list:
        #     rand_dir = os.path.join(temp_dir, rand)
        #     shutil.rmtree(rand_dir)
        # -------------------------------------------------

        return offsets, align_errors

    else:
        return offsets
