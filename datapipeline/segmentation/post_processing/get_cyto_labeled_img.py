import argparse
import subprocess
import tifffile
import glob
import os
import numpy as np
from PIL import Image
import pip
import tempfile
import cv2
import sys
import time
import imageio

from ...helpers.rand_list import get_random_list, are_jobs_finished


from ...load_tiff import tiffy

USER = os.getenv('USER')

def max_intensity_projection(cyto_3d):
    IM_MAX= np.max(cyto_3d, axis=0)
    return IM_MAX

def get_labeled_cyto_cellpose(tiff_path, num_wav, dst=None, cyto_channel = -2, debug = False, cell_prob_threshold = 0, cell_flow_threshold = .4, cyto_radius = 0):


    #Getting Tiff
    #----------------------------------------------
    print('Reading TIff')
    tiff = tiffy.load(tiff_path,num_wav)
    file_name = os.path.basename(tiff_path)
    dir_name = os.path.dirname(tiff_path)
    #----------------------------------------------
    
    print('Shrinking TIff')
    #Get Shrinked Dapi Channel
    #----------------------------------------------
    print(f'{cyto_channel=}')
    cyto_channel = cyto_channel - 1
    cyto_3d = tiff[:, cyto_channel,:,:].astype(np.int16)

    max_cyto_2d = max_intensity_projection(cyto_3d)
    
    print("Running Image Processing Before Segmentation (This may take some time)")

    shrinked = (np.array(Image.fromarray(max_cyto_2d).resize((512, 512))))
    #----------------------------------------------
    
    
    #Save to temp directory
    #----------------------------------------------
    dst_dir = '/groups/CaiLab/personal/temp/temp_seg'
    rand_list = get_random_list(1)
    rand_dir = os.path.join(dst_dir, rand_list[0])
    os.mkdir(rand_dir)
    dapi_tiff_dst = os.path.join(rand_dir,  'dapi_channel_2d.tif')
    tifffile.imsave(dapi_tiff_dst, shrinked)
    #----------------------------------------------


    #Commands to be run for cellpose
    #----------------------------------------------
    bind_paths = f'/central/scratch/{USER},' \
                 f'/groups/CaiLab/personal/temp,' \
                 f'/groups/CaiLab/personal/singularity/lib/python3.6/site-packages' \
                 f':/usr/lib/python3.6/site-packages'

    sing_and_cellpose_cmd = f'singularity  exec --bind {bind_paths} ' \
                            f'--nv /groups/CaiLab/personal/singularity/tensorflow-20.02-tf1-py3.sif' \
                            f' python -m cellpose '

    persistent_params = ' --img_filter dapi_channel_2d --pretrained_model cyto --use_gpu --no_npy --save_png '
    cyto_cell_prob_thresh_cmd = ' --cellprob_threshold ' + str(cell_prob_threshold)
    cyto_flow_thresh_cmd = ' --flow_threshold ' + str(cell_flow_threshold) 
    diameter_cmd = ' --diameter ' + str(cyto_radius)
    #----------------------------------------------
    
    
    #Combinining commands
    #----------------------------------------------
    command_for_cellpose= sing_and_cellpose_cmd + persistent_params + cyto_cell_prob_thresh_cmd + cyto_flow_thresh_cmd + diameter_cmd + ' --dir '
    command_for_cellpose_with_dir = command_for_cellpose + rand_dir
    print(f'{command_for_cellpose_with_dir=}')
    #----------------------------------------------
    
    #Write command to .sh script and run
    #----------------------------------------------
    script_name = os.path.join(rand_dir, 'seg.sh')
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write('#SBATCH --gres=gpu:1 \n')
        f.write(command_for_cellpose_with_dir)

    call_me = ['sbatch', '--job-name', rand_list[0], "--time", "1:00:00", "--mem-per-cpu", "10G", script_name]
    subprocess.call(call_me)
    #----------------------------------------------

    #Wait to see if job is finished
    #----------------------------------------------
    while not are_jobs_finished(rand_list):
        print('Waiting for Segmenation to Finish')
        time.sleep(2)
    #----------------------------------------------
    
    print(f'{rand_dir=}')
    #Read in masked file
    #----------------------------------------------
    masked_file_path = os.path.join(rand_dir, 'dapi_channel_2d_cp_masks.png')
    labeled_img = imageio.imread(masked_file_path)
    print(f'{labeled_img.shape=}')
    #----------------------------------------------
    
    
    #Get resize script
    #----------------------------------------------
    resize_script = os.path.join(os.path.dirname(__file__), 'nucsmoothresize')
    #----------------------------------------------


    subprocess.call([resize_script, masked_file_path, str(tiff.shape[2]), dst])
    labeled_img = imageio.imread(dst) 
    

    return labeled_img


if __name__ == '__main__':

    if sys.argv[1] == 'debug_cellpose_cyto':

        labeled_img = get_labeled_cyto_cellpose(tiff_path='/groups/CaiLab/personal/nrezaee/raw/intron_pos0/HybCycle_0/MMStack_Pos0.ome.tif',
                                                num_wav = 4,
                                                dst = 'foo.tif',
                                                debug = True,
                                                cyto_radius = 10)