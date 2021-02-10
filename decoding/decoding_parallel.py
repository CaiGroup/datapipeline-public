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
import cv2
import pickle
import matplotlib.pyplot as plt
import sys

import sys
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')

debug = False

print(f'{sys.argv=}')

if sys.argv[1] == 'debug':
    os.chdir('decoding')
    from helpers.parallel.seg_locs import get_segmentation_dict_dots, get_labeled_img
    from helpers.parallel.rand_list import are_jobs_finished, get_random_list
    from helpers.parallel.combine_csv_s import get_combined_csv
    os.chdir('../')
    print(f'{os.getcwd()=}')
else:
    from decoding.helpers.parallel.seg_locs import get_segmentation_dict_dots, get_labeled_img
    from decoding.helpers.parallel.rand_list import are_jobs_finished, get_random_list
    from decoding.helpers.parallel.combine_csv_s import get_combined_csv

def get_barcode_info(barcode_src):

    print("Reading Barcode Key")
    
    barcodes = loadmat(barcode_src)["barcodekey"]

    num_of_rounds = barcodes[0][0][0].shape[1]
    
    channels_per_round = np.max(barcodes[0][0][0][:200])
    
    total_number_of_channels = num_of_rounds*channels_per_round
    
    assert total_number_of_channels % num_of_rounds == 0
    
    return total_number_of_channels, num_of_rounds
    
def save_plotted_cell(labeled_img, points, fig_dest):
    plt.figure(figsize=(30,30))

    #print(f'{points=}')
    print(f'{points.shape=}')

    ave_z = int((np.max(points[:,0]) + np.min(points[:,0]))//2)
    if ave_z < labeled_img.shape[0]:
        print(f'{ave_z=}')
        plt.imshow(labeled_img[ave_z,:,:])
        plt.scatter(points[:,1][:100], points[:,2][:100], s=10, color='red')
        print(f'{fig_dest=}')
        plt.savefig(fig_dest)

    

def run_matlab_decoding(rand, barcode_src, locations_cell_path, dest, num_of_rounds, allowed_diff, min_seeds, total_number_of_channels, channel_index, number_of_individual_channels_for_decoding):           
    #Create Matlab Command
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """ 
    
    cwd = os.getcwd()
    
    print(f'{cwd=}')
    
    
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    
    if debug:
        decoding_dir = os.path.join(cwd, 'helpers')
    else:
        decoding_dir = os.path.join(cwd, 'decoding', 'helpers')
        

    
    
    if channel_index == None and number_of_individual_channels_for_decoding == None:
        
        print(f'{min_seeds=}')
        
        cmd = cmd.format(decoding_dir, barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels, '[]', '[]', allowed_diff, min_seeds)
        
        
        print(f'{cmd=}')
    else:
        
        print(f'{type(channel_index)=}')
        print(f'{type(number_of_individual_channels_for_decoding)=}')
        
        print(f'{channel_index=}')
        print(f'{number_of_individual_channels_for_decoding=}')
        
    
        cmd = cmd.format(decoding_dir, barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels, \
        channel_index+1, number_of_individual_channels_for_decoding, allowed_diff, min_seeds)
        
    #-------------------------------------------------------------------
    
    
    script_name = os.path.join(dest, 'decoding.sh')
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write(cmd)
    
    output_path = os.path.join(dest, 'slurm_decoding.out')
    call_me = ['sbatch','--job-name', rand, "--output", output_path, "--time", "0:50:00", "--mem-per-cpu", "8G",  '--ntasks', '1', script_name]
    print(" ".join(call_me))
    subprocess.call(call_me)
    
def decoding(barcode_src ,locations_src, labeled_img, dest, allowed_diff, min_seeds, channel_index = None, \
        number_of_individual_channels_for_decoding=None, roi_path=None, bool_cellpose=False, decode_only_cells = False):
    
    
    print(f'{labeled_img.shape=}')
    total_number_of_channels, num_of_rounds = get_barcode_info(barcode_src)
    
    
    plotted_img_dest = os.path.join(dest, 'Plotted_Cell_Spot_Locations.png')
    seg_dict = get_segmentation_dict_dots(locations_src, labeled_img, plotted_img_dest)
    
    if decode_only_cells == True:
        del seg_dict[0]
    

    rand_list = get_random_list(len(seg_dict.keys()))
    
    cell_dirs = []
    
    for i in range(len(seg_dict.keys())):

        print("Saving locations")
        #Get and Save Location in Dict Key
        #-------------------------------------------------------------------
        locations_for_cell = np.array(seg_dict[list(seg_dict.keys())[i]])

        cell_dirs.append('cell_' +str(i))
        temp_dir = os.path.join(dest, 'cell_' + str(i)) 
        os.mkdir(temp_dir)
        locations_cell_path = os.path.join(temp_dir, 'locations_for_cell.mat')

        savemat(locations_cell_path, {'points':locations_for_cell[:,0], 'intensity':locations_for_cell[:,1]})
        temp_dest =temp_dir
        #-------------------------------------------------------------------
        
        run_matlab_decoding(rand_list[i], barcode_src, locations_cell_path, temp_dest, num_of_rounds, allowed_diff, min_seeds, total_number_of_channels, channel_index, number_of_individual_channels_for_decoding)         

    #Check if Jobs are Finished
    #-----------------------------------------------------------------------------
    while not are_jobs_finished(rand_list):
        print(f'Waiting for Decoding Jobs to Finish')
        time.sleep(10)
        
    print(f'{rand_list=}')
    #-----------------------------------------------------------------------------
    
    if min_seeds =='number_of_rounds - 1':
        min_seeds = num_of_rounds - 1
        
    dest_unfilt = os.path.join(dest, 'pre_seg_diff_' + str(allowed_diff) + '_minseeds_'+ str(min_seeds)+ '_unfiltered.csv')
    dest_filt = os.path.join(dest, 'pre_seg_diff_' + str(allowed_diff) + '_minseeds_'+ str(min_seeds)+ '_filtered.csv')
    get_combined_csv(dest, cell_dirs, dest_unfilt, dest_filt)
    
    return rand_list
    

# if sys.argv[1] == 'debug':
#     import tifffile 
    
#     labeled_img_src = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_mat_dapi/MMStack_Pos0/Segmentation/Channel_1/labeled_img.tiff'
#     barcode_src = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_1000/BarcodeKey/channel_1.mat'
#     locations_src = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_1000/MMStack_Pos0/Dot_Locations/locations.mat'
    
#     dest = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/temp/'
#     allowed_diff = 0
#     min_seeds = 3
    
#     labeled_img = tifffile.imread(labeled_img_src)
#     decoding(barcode_src ,locations_src, labeled_img, dest, allowed_diff, min_seeds)


