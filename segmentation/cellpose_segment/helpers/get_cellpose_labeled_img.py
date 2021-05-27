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

    #Flip each image
    #------------------------------------
    for z in range(labeled_img.shape[0]):
        labeled_img[z] = cv2.flip(labeled_img[z], 0)
    #------------------------------------    

    return labeled_img
    
def get_shrinked(tiff):
    
    #Get dapi_tiff
    #------------------------------------
    dapi_channel = -1
    dapi_tiff = tiff[:,dapi_channel,:,:].astype(np.int16)
    #------------------------------------
    
    
    #Shrink the image
    #------------------------------------
    print("Running Image Processing Before Segmentation (This may take some time)")
    shrinked = []
    print(f'{tiff.shape=}')
    for i in range(dapi_tiff.shape[0]):
        print("    Processing on Z Slice ", i)
        shrinked.append(np.array(Image.fromarray(dapi_tiff[i]).resize((512, 512))))
    #------------------------------------
    
    return shrinked

def save_shrinked(shrinked):
    
    #Make random file
    #------------------------------------
    dst_dir = '/home/nrezaee/temp'
    rand_list = get_random_list(1)
    rand_dir = os.path.join(dst_dir, rand_list[0])
    os.mkdir(rand_dir)
    #------------------------------------
    
    #Save randome file
    #------------------------------------
    dapi_tiff_dst = os.path.join(rand_dir,  'dapi_channel.tif')
    tifffile.imsave(dapi_tiff_dst, shrinked)
    #------------------------------------
    
    return rand_list, rand_dir, dapi_tiff_dst
    
def submit_seg_job(rand_dir, rand_list, num_z, nuclei_radius, flow_threshold, cell_prob_threshold):
    
    print("Running Segmentation with SLURM GPU's")

    
    #Set Cellpose Parameters
    #---------------------------------------------------------------------------
    diameter_param = ' --diameter ' + str(float(nuclei_radius)*2)
    flow_thresh_param = ' --flow_threshold ' + str(flow_threshold)
    cell_prob_thresh_param = ' --cellprob_threshold ' + str(cell_prob_threshold)
    #---------------------------------------------------------------------------
    
    #Set command and default params
    #---------------------------------------------------------------------------
    sing_and_cellpose_cmd = 'singularity  exec --bind /central/scratch/$USER --nv /groups/CaiLab/personal/nrezaee/tensorflow-20.02-tf1-py3.sif python -m cellpose '
    default_params = ' --img_filter dapi_channel --pretrained_model cyto --use_gpu --no_npy --save_tif --dir '
    #---------------------------------------------------------------------------
    
    #Determine whether or not to run 2d or 3d segmentation
    #---------------------------------------------------------------------------
    if num_z >= 4:
        command_for_cellpose= sing_and_cellpose_cmd + ' --do_3D' + diameter_param + flow_thresh_param + \
                            cell_prob_thresh_param + default_params
    if num_z < 4:
        command_for_cellpose= sing_and_cellpose_cmd + diameter_param + flow_thresh_param + \
                            cell_prob_thresh_param + default_params
    #---------------------------------------------------------------------------
    
    #Make cellpose command
    #---------------------------------------------------------------------------
    command_for_cellpose_with_dir = command_for_cellpose + rand_dir
    print(f'{command_for_cellpose_with_dir=}')
    script_name = os.path.join(rand_dir, 'seg.sh')
    #---------------------------------------------------------------------------
    
    #Make and run batch script
    #---------------------------------------------------------------------------
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write('#SBATCH --gres=gpu:1 \n')
        f.write(command_for_cellpose_with_dir)

    call_me = ['sbatch', '--job-name', rand_list[0], "--time", "0:05:00", "--mem-per-cpu", "5G", script_name]
    subprocess.call(call_me)
    #---------------------------------------------------------------------------
    
    
def expand_img(masked_file_path, tiff, dst):
    
    #Create and run resize script
    #---------------------------------------------------------------------------
    resize_script = os.path.join('/home/nrezaee/test_cronjob_multi_dot/segmentation/cellpose_segment/helpers/nucsmoothresize')
    cmd = ' '.join(['sh', resize_script, masked_file_path, str(tiff.shape[2]), dst])
    print(f'{cmd=}')
    os.system(cmd)
    #---------------------------------------------------------------------------
    
    #Load and return expanded tif
    #---------------------------------------------------------------------------
    labeled_img = tifffile.imread(dst)
    return labeled_img
    #---------------------------------------------------------------------------
    
def get_3d_from_2d(src, num_z):
    
    #Stack 2d into 3d
    #---------------------------------------------------------------------------
    tiff_2d = tf.imread(src)
    tiff_3d = []
    for z in range(num_z):
        tiff_3d.append(tiff_2d)
    #---------------------------------------------------------------------------

    #Save tif
    #---------------------------------------------------------------------------
    #tiff_3d = np.swapaxes(tiff_3d, 0, 2)
    tf.imwrite(src, tiff_3d)
    #---------------------------------------------------------------------------
    
def get_labeled_img_cellpose(tiff_path, num_wav, dst=None, nuclei_radius=0, flow_threshold =.4, cell_prob_threshold=0):


    #Getting Tiff
    #----------------------------------------------
    print('Reading TIff')
    tiff = tiffy.load(tiff_path, num_wav)
    file_name = os.path.basename(tiff_path)
    dir_name = os.path.dirname(tiff_path)
    #----------------------------------------------
    
    #Shrink and save tif
    #---------------------------------------------------------------------------
    shrinked = get_shrinked(tiff)
    #shrinked.shape = [z,x,y]
    rand_list, rand_dir, dapi_tiff_dst = save_shrinked(shrinked)
    #---------------------------------------------------------------------------
    
    
    #Submit job and wait for it to finish
    #---------------------------------------------------------------------------
    num_z = len(shrinked)
    submit_seg_job(rand_dir, rand_list, num_z, nuclei_radius, flow_threshold, cell_prob_threshold)

    while not are_jobs_finished(rand_list):
        print('Waiting for Segmenation to Finish')
        time.sleep(2)
    
    masked_file_path = os.path.join(rand_dir, 'dapi_channel_cp_masks.tif')
    #---------------------------------------------------------------------------
    
    
    #Make 2d into 3d if 2d
    #---------------------------------------------------------------------------
    if num_z < 4:
        get_3d_from_2d(masked_file_path, num_z)
    #---------------------------------------------------------------------------
        
    #Save to destination
    #---------------------------------------------------------------------------
    if dst == None:
        temp_path = os.path.join(rand_dir, 'expanded.tif')
        labeled_img = expand_img(masked_file_path, tiff, temp_path)
    else:
        labeled_img = expand_img(masked_file_path, tiff, dst)
    #---------------------------------------------------------------------------
    
    shutil.rmtree(rand_dir)

    return labeled_img

if sys.argv[1] == 'debug_cellpose':
    labeled_img = get_labeled_img_cellpose(tiff_path = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_1/MMStack_Pos0.ome.tif', 
                                            num_wav = 4,
                                            dst = '/home/nrezaee/temp/labeled_img_thresh_3.tif', 
                                            nuclei_radius=20)
    print(f'{labeled_img.shape=}')
    
    
    
