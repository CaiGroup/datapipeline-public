import os
import glob
import multiprocessing
import pickle
import subprocess
import time
import shutil


#Import Multiprocessing helper
#-------------------------------------------------
from align_scripts.helpers.rand_list import are_jobs_finished, get_random_list
from align_scripts.helpers.combine_offs import combine_offsets
from align_scripts.helpers.combine_offs import combine_align_errors
#-------------------------------------------------



main_dir = '/groups/CaiLab'


def get_and_sort_hybs(path_to_experiment_dir):
    
    
    #Get all files in path
    #-------------------------------------------------
    hyb_dirs = glob.glob(path_to_experiment_dir)
    #-------------------------------------------------
    
    
    #Remove anything that is not a Hyb
    #-------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in hyb_dirs if 'HybCycle' in hyb_dir]
    #-------------------------------------------------
    
    
    #Split hybs to get numbers
    #-------------------------------------------------
    split_word = 'Cycle_'
    for index in range(len(hyb_dirs)):

        hyb_dirs[index] = hyb_dirs[index].split(split_word)
 
        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    #-------------------------------------------------
    
    
    #Sort the Hybs
    #-------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    #-------------------------------------------------

    
    #Combine the strings to right format
    #-------------------------------------------------
    for index in range(len(sorted_hyb_dirs)):
        sorted_hyb_dirs[index][1] = str(sorted_hyb_dirs[index][1])
        sorted_hyb_dirs[index].insert(1, split_word)
        sorted_hyb_dirs[index] = ''.join(sorted_hyb_dirs[index])
    #-------------------------------------------------
    
    return sorted_hyb_dirs
    
def get_fixed_and_movings(exp_name, personal, position, main_dir):
    
    exp_dir = os.path.join(main_dir, 'personal',personal, 'raw', exp_name)
    
    #offsets = {}
    
    sub_dirs = get_and_sort_hybs(os.path.join(exp_dir,'*'))
    
    fixed_hyb = sub_dirs[0].split(os.sep)[-1]
    
    fixed_file_path = os.path.join(exp_dir, fixed_hyb, position)    
    
    return sub_dirs, fixed_file_path

def run_alignment(exp_name, personal, position, align_function, num_wav):
    
    
    sub_dirs, fixed_file_path = get_fixed_and_movings(exp_name, personal, position, main_dir)
    
    rand_list = get_random_list(len(sub_dirs))
    
    
    cwd = os.getcwd()
    align_dir = os.path.join(cwd, 'align_scripts',)
    
    temp_dir = os.path.join(main_dir, 'personal', 'temp', 'temp_align')
    
    if align_function == 'no_align':
        offsets = {}
    
    #Run alignment
    #-----------------------------------------------------------------
    for sub_dir in sub_dirs:
            
        tiff_file_path = os.path.join(sub_dir, position)    
        
        #Print Statement
        #-----------------------------------------------------------------
        hyb = sub_dir.split(os.sep)[-1]
        if align_function != 'no_align':
            print("    Running Alignment on", hyb, 'for', position, flush=True)
        #-----------------------------------------------------------------
  
        
        #Declare Random Dir
        #-----------------------------------------------------------------
        rand = rand_list[sub_dirs.index(sub_dir)]
        temp_dir = os.path.join(main_dir, 'personal', 'temp', 'temp_align')
        rand_dir = os.path.join(temp_dir, rand)
        try:
            os.mkdir(rand_dir)
        except FileExistsError:
            pass
        #-----------------------------------------------------------------
        
        if align_function == 'no_align':
            key = os.path.join(hyb, position)
            offsets[key] = [0,0,0]
            
        elif align_function == 'fiducial_markers':
            pass 
        
            
        else:
            print(f'{tiff_file_path=}')
            list_cmd = ['python', align_dir+ '/'+align_function+ '.py', '--fixed_src', fixed_file_path, '--moving_src', tiff_file_path, '--rand', rand_dir, '--num_wav', str(num_wav)]
        
    
            cmd = ' '.join(list_cmd)
    
            script_name = os.path.join(rand_dir, 'align.sh')
            out_file_path = script_name = os.path.join(rand_dir, 'slurm_align.out')
            with open(script_name , 'w') as f:
                f.write('#!/bin/bash \n')
                f.write(cmd)
            
    
            call_me = ['sbatch', '--output', out_file_path, '--job-name', rand_list[sub_dirs.index(sub_dir)], "--time", "0:20:00","--mem-per-cpu", "9G", "--ntasks", '1', script_name ]
            print(f'{" ".join(call_me)=}')
            subprocess.call(call_me)

    if align_function != 'no_align':
        print(f'{rand_list=}')
        
        while not are_jobs_finished(rand_list):
            print('Waiting for Alignment Jobs to Finish')
            time.sleep(30)
        
        offsets = combine_offsets(rand_list)
        
        align_errors = combine_align_errors(rand_list)
        
 
        #Delete Temp files
        for rand in rand_list:
            rand_dir = os.path.join(temp_dir, rand)
            shutil.rmtree(rand_dir)
            
        return offsets, align_errors
        
    else:
        return offsets
    
    
    
    