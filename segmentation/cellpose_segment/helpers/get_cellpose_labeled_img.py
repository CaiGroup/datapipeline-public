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
import shutil
import tifffile as tf

sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from helpers.rand_list import get_random_list, are_jobs_finished
from load_tiff import tiffy


    
def correct_labeled_img(labeled_img):

    
    for z in range(labeled_img.shape[0]):
       # labeled_img[z] = ndimage.rotate(labeled_img[z], -90)
        labeled_img[z] = cv2.flip(labeled_img[z], 0)
        #labeled_img[z] = ndimage.rotate(labeled_img[z], -90)
        

    return labeled_img
    
def get_shrinked(tiff):
    
    dapi_channel = -1
    dapi_tiff = tiff[:,dapi_channel,:,:].astype(np.int16)
    
    shrinked = []
    
    print("Running Image Processing Before Segmentation (This may take some time)")
    
    print(f'{tiff.shape=}')
    for i in range(dapi_tiff.shape[0]):
        print("    Processing on Z Slice ", i)
        shrinked.append(np.array(Image.fromarray(dapi_tiff[i]).resize((512, 512))))
        
    return shrinked

def save_shrinked(shrinked):
    dst_dir = '/home/nrezaee/temp'
    rand_list = get_random_list(1)
    rand_dir = os.path.join(dst_dir, rand_list[0])
    os.mkdir(rand_dir)
    dapi_tiff_dst = os.path.join(rand_dir,  'dapi_channel.tif')
    tifffile.imsave(dapi_tiff_dst, shrinked)
    
    return rand_list, rand_dir, dapi_tiff_dst
    
def submit_seg_job(rand_dir, rand_list, num_z):
    
    print("Running Segmentation with SLURM GPU's")
    
    if num_z >= 4:
        command_for_cellpose= 'singularity  exec --bind /central/scratch/$USER --nv /home/nrezaee/sandbox/cellpose/gpu/tensorflow-20.02-tf1-py3.sif python -m cellpose  --do_3D --img_filter dapi_channel --pretrained_model cyto --diameter 0 --use_gpu --no_npy --save_tif --dir '
    if num_z < 4:
        command_for_cellpose= 'singularity  exec --bind /central/scratch/$USER --nv /home/nrezaee/sandbox/cellpose/gpu/tensorflow-20.02-tf1-py3.sif python -m cellpose   --img_filter dapi_channel --pretrained_model cyto --diameter 0 --use_gpu --no_npy --save_tif --dir '
    
    command_for_cellpose_with_dir = command_for_cellpose + rand_dir
    print(f'{command_for_cellpose_with_dir=}')
    script_name = os.path.join(rand_dir, 'seg.sh')
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write('#SBATCH --gres=gpu:1 \n')
        f.write(command_for_cellpose_with_dir)

    call_me = ['sbatch', '--job-name', rand_list[0], "--time", "0:05:00", "--mem-per-cpu", "5G", script_name]
    subprocess.call(call_me)
    
def expand_img(masked_file_path, tiff, dst):
    resize_script = os.path.join('/home/nrezaee/test_cronjob_multi_dot/segmentation/cellpose_segment/helpers/nucsmoothresize')
    
    cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), dst])
    print(f'{cmd=}')
    os.system(cmd)
    labeled_img = tifffile.imread(dst)
    return labeled_img
    
def get_3d_from_2d(src, num_z):
    tiff_2d = tf.imread(src)

    tiff_3d = []
    for z in range(num_z):
        tiff_3d.append(tiff_2d)

    tf.imwrite(src, tiff_3d)
    
def get_labeled_img_cellpose(tiff_path, dst=None):


    #Getting Tiff
    #----------------------------------------------
    print('Reading TIff')
    tiff = tiffy.load(tiff_path)
    file_name = os.path.basename(tiff_path)
    dir_name = os.path.dirname(tiff_path)
    #----------------------------------------------
    
    shrinked = get_shrinked(tiff)
    #shrinked.shape = [z,x,y]

    
    rand_list, rand_dir, dapi_tiff_dst = save_shrinked(shrinked)
    
    num_z = len(shrinked)
    submit_seg_job(rand_dir, rand_list, num_z)

    while not are_jobs_finished(rand_list):
        print('Waiting for Segmenation to Finish')
        time.sleep(2)
    
    masked_file_path = os.path.join(rand_dir, 'dapi_channel_cp_masks.tif')
    
    if num_z < 4:
        get_3d_from_2d(masked_file_path, num_z)
        
        
    resize_script = os.path.join('/home/nrezaee/test_cronjob_multi_dot/segmentation/cellpose_segment/helpers/nucsmoothresize')
    
    if dst == None:
        temp_path = os.path.join(rand_dir, 'expanded.tif')
        labeled_img = expand_img(masked_file_path, tiff, temp_path)
    else:
        labeled_img = expand_img(masked_file_path, tiff, dst)
    
    shutil.rmtree(rand_dir)

    return labeled_img

if sys.argv[1] == 'debug_cellpose':
    tiff_path = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_1/MMStack_Pos0.ome.tif'
    dst= '/home/nrezaee/temp/labeled_img_thresh_3.tif'
    labeled_img = get_labeled_img_cellpose(tiff_path, dst)
    print(f'{dst=}')
    print(f'{labeled_img.shape=}')
    
    
    
