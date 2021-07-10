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

sys.path.insert(0, os.getcwd())
from helpers.rand_list import get_random_list, are_jobs_finished


from load_tiff import tiffy



def get_labeled_cyto_cellpose(tiff_path, dst=None):


    #Getting Tiff
    #----------------------------------------------
    print('Reading TIff')
    tiff = tiffy.load(tiff_path)
    file_name = os.path.basename(tiff_path)
    dir_name = os.path.dirname(tiff_path)
    #----------------------------------------------
    
    print('Shrinking TIff')
    #Get Shrinked Dapi Channel
    #----------------------------------------------
    dapi_channel = -1
    dapi_tiff = tiff[tiff.shape[0]//2, dapi_channel,:,:].astype(np.int16)
    

    print("Running Image Processing Before Segmentation (This may take some time)")
    


    shrinked = (np.array(Image.fromarray(dapi_tiff).resize((512, 512))))
    #----------------------------------------------
    
    
    
    #Save to temp directory
    #----------------------------------------------
    dst_dir = '/home/nrezaee/temp'
    rand_list = get_random_list(1)
    rand_dir = os.path.join(dst_dir, rand_list[0])
    os.mkdir(rand_dir)
    dapi_tiff_dst = os.path.join(rand_dir,  'dapi_channel_2d.tif')
    tifffile.imsave(dapi_tiff_dst, shrinked)
    #----------------------------------------------


    #Save Command to file and run
    #----------------------------------------------
    print("Running Segmentation with SLURM GPU's")

    command_for_cellpose= 'singularity  exec --bind /central/scratch/$USER --nv /home/nrezaee/sandbox/cellpose/gpu/tensorflow-20.02-tf1-py3.sif python -m cellpose  --img_filter dapi_channel_2d --pretrained_model cyto --diameter 0 --use_gpu --no_npy --save_png --dir '
    command_for_cellpose_with_dir = command_for_cellpose + rand_dir
    print(f'{command_for_cellpose_with_dir=}')
    script_name = os.path.join(rand_dir, 'seg.sh')
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write('#SBATCH --gres=gpu:1 \n')
        f.write(command_for_cellpose_with_dir)

    call_me = ['sbatch', '--job-name', rand_list[0], "--time", "1:00:00", "--mem-per-cpu", "10G", script_name]
    subprocess.call(call_me)
    #----------------------------------------------
    
    while not are_jobs_finished(rand_list):
        print('Waiting for Segmenation to Finish')
        time.sleep(1)
    
    #----------------------------------------------
    
    print(f'{rand_dir=}')
    #Change name of masked file
    #----------------------------------------------
    
    
    masked_file_path = os.path.join(rand_dir, 'dapi_channel_2d_cp_masks.png')
    
    labeled_img = imageio.imread(masked_file_path)
    print(f'{labeled_img=}')
    
    # labeled_img = expand_img(labeled_img)
    resize_script = os.path.join(os.getcwd(), 'segmentation/cellpose_segment/helpers/nucsmoothresize')
    

    if dst == None:
        temp_path = os.path.join(rand_dir, 'expanded.tif')
        
        cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), temp_path])
        print(f'{cmd=}')
        os.system(cmd)
        labeled_img = tifffile.imread(temp_path)
        
    else:
        subprocess.call(['sh', resize_script, masked_file_path, str(tiff.shape[2]), dst])
        labeled_img = imageio.imread(dst) 
    

    return labeled_img

# tiff_path = '/groups/CaiLab/personal/nrezaee/raw/intron_pos0/HybCycle_0/MMStack_Pos0.ome.tif'
# mini_tiff_path = '/groups/CaiLab/personal/nrezaee/raw/test1/HybCycle_1/MMStack_Pos0.ome.tif'
# dst = 'labeled_cyto.tif'
# labeled_img = get_labeled_cyto_cellpose(tiff_path, dst)
# print(f'{np.unique(labeled_img)=}')
    
