import tempfile
import os
import numpy as np
from scipy.io import loadmat, savemat
import multiprocessing
import string
import random
import time
import subprocess
import getpass
import glob
import tifffile

from decoding.helpers.parallel.seg_locs import get_segmentation_dict_dots, get_labeled_img
from decoding.helpers.parallel.rand_list import are_jobs_finished, get_random_list
from decoding.helpers.parallel.combine_csv_s import get_combined_csv

def decoding(barcode_src ,locations_src, labeled_img, dest, allowed_diff, min_seeds, channel_index = None, number_of_individual_channels_for_decoding=None, roi_path=None, bool_cellpose=False):
    
    
    print("Reading Barcode Key")
    #Get rounds and channels of experiment
    #-------------------------------------------------------------------
    barcodes = loadmat(barcode_src)["barcodekey"]

    num_of_rounds = barcodes[0][0][0].shape[1]
    
    channels_per_round = np.max(barcodes[0][0][0][:200])
    
    total_number_of_channels = num_of_rounds*channels_per_round
    #-------------------------------------------------------------------
    
    
    #Check if total channels is divisible by rounds
    #-------------------------------------------------------------------
    assert total_number_of_channels % num_of_rounds == 0
    #-------------------------------------------------------------------
    
    
    #Segmentation
    #-------------------------------------------------------------------
    # if roi_path != None:
        
    print("Segmenting Dots")
    print(f'{np.unique(labeled_img)=}')
    seg_dict = get_segmentation_dict_dots(locations_src, labeled_img)
    #-------------------------------------------------------------------
        
    
    #Get Random List
    #-------------------------------------------------------------------
    rand_list = get_random_list(len(seg_dict.keys()))
    #-------------------------------------------------------------------
    
    for i in range(len(seg_dict.keys())):
        
        print("Saving locations")
        #Get and Save Location in Dict Key
        #-------------------------------------------------------------------
        locations_for_cell = seg_dict[list(seg_dict.keys())[i]]
        #temp_dir = tempfile.TemporaryDirectory()
        dir_of_temp_dirs = '/groups/CaiLab/personal/nrezaee/temp'
        temp_dir = os.path.join(dir_of_temp_dirs, rand_list[i]) 
        os.mkdir(temp_dir)
        locations_cell_path = os.path.join(temp_dir, 'locations_for_cell.mat')
        
        savemat(locations_cell_path, {'locations':locations_for_cell})
        temp_dest =temp_dir
        #-------------------------------------------------------------------
        
    
        def run_matlab_decoding(barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels, channel_index, number_of_individual_channels_for_decoding):           
            #Create Matlab Command
            #-------------------------------------------------------------------
            cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """ 
            
            cwd = os.getcwd()
            
            print(f'{cwd=}')
            
            
            cwd = cwd[cwd.find('/home'):]
            print(f'{cwd=}')
            
            decoding_dir = os.path.join(cwd, 'decoding')
            decoding_dir = '/home/nrezaee/test_cronjob_multi/decoding/helpers'
            
            if channel_index == None and number_of_individual_channels_for_decoding == None:
                
                print(f'{min_seeds=}')
                
                cmd = cmd.format(decoding_dir, barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels, '[]', '[]', allowed_diff, min_seeds)
                
                
                print(f'{cmd=}')
            else:
                
                print(f'{type(channel_index)=}')
                print(f'{type(number_of_individual_channels_for_decoding)=}')
                
                print(f'{channel_index=}')
                print(f'{number_of_individual_channels_for_decoding=}')
                
            
                cmd = cmd.format(decoding_dir, barcode_src, locations_src, temp_dest, num_of_rounds, total_number_of_channels, \
                channel_index+1, number_of_individual_channels_for_decoding, allowed_diff, min_seeds)
                
            #-------------------------------------------------------------------
            
            
            script_name = os.path.join(temp_dir, 'decoding.sh')
            with open(script_name , 'w') as f:
                f.write('#!/bin/bash \n')
                f.write(cmd)
         
            call_me = ['sbatch','--job-name', rand_list[i], "--time", "1:00:00", "--mem-per-cpu", "10G", script_name]
            print(" ".join(call_me))
            subprocess.call(call_me)
            #Run Matlab Command
            #-------------------------------------------------------------------
            #os.system(cmd)
            #-------------------------------------------------------------------
            
        run_matlab_decoding(barcode_src, locations_cell_path, temp_dest, num_of_rounds, total_number_of_channels, channel_index, number_of_individual_channels_for_decoding)         

    #Check if Jobs are Finished
    #-----------------------------------------------------------------------------
    while not are_jobs_finished(rand_list):
        print(f'Waiting for Decoding Jobs to Finish')
        time.sleep(.1)
        
    print(f'{rand_list=}')
    #-----------------------------------------------------------------------------
    
    if min_seeds =='number_of_rounds - 1':
        min_seeds = num_of_rounds - 1
        
    dest_unfilt = os.path.join(dest, 'pre_seg_diff_' + str(allowed_diff) + '_minseeds_'+ str(min_seeds)+ '_unfiltered.csv')
    dest_filt = os.path.join(dest, 'pre_seg_diff_' + str(allowed_diff) + '_minseeds_'+ str(min_seeds)+ '_filtered.csv')
    get_combined_csv(rand_list, dest_unfilt, dest_filt)
    
    return rand_list
    
  


