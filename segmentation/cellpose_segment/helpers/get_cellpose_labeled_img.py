
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

USER = os.getenv('USER')
sys.path.insert(0, os.getcwd())
from helpers.rand_list import get_random_list, are_jobs_finished
from load_tiff import tiffy



def correct_labeled_img(labeled_img):

    #Flip each image
    #------------------------------------
    for z in range(labeled_img.shape[0]):
        labeled_img[z] = cv2.flip(labeled_img[z], 0)
    #------------------------------------

    return labeled_img

def get_shrinked(tiff, dapi_channel):

    print(f'{dapi_channel=}')
    #Get dapi_tiff
    #------------------------------------
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
    #dst_dir = '/home/lombelet/temp'
    dst_dir = '/groups/CaiLab/personal/temp/temp_seg'
    rand_list = get_random_list(1)
    rand_dir = os.path.join(dst_dir, rand_list[0])
    os.mkdir(rand_dir)
    #------------------------------------

    #Save randome file
    #------------------------------------
    dapi_tiff_dst = os.path.join(rand_dir,  'dapi_channel.tif')
    tifffile.imsave(dapi_tiff_dst, shrinked)
    #------------------------------------

    import time; time.sleep(1)

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
    bind_paths = f'/central/scratch/{USER},/groups/CaiLab/personal/temp,/home/lombelet/.local/lib/python3.6/site-packages:/usr/lib/python3.6/site-packages'
    sing_and_cellpose_cmd = f'singularity  exec --bind {bind_paths} --nv /groups/CaiLab/personal/lincoln/tensorflow-20.02-tf1-py3.sif python -m cellpose '
    default_params = ' --img_filter dapi_channel --pretrained_model cyto --use_gpu --no_npy --save_tif --dir '
    import time; time.sleep(1)
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

    #Set Slurm out dst
    #---------------------------------------------------------------------------
    slurm_out_dst = os.path.join(rand_dir, 'slurm_seg.out')
    #---------------------------------------------------------------------------

    #Change permissions
    #---------------------------------------------------------------------------
    os.system('chmod 777 ' +  rand_dir)
    os.system('chmod 777 -R ' +  rand_dir)
    #---------------------------------------------------------------------------


    #Make and run batch script
    #---------------------------------------------------------------------------
    with open(script_name , 'w') as f:
        f.write('#!/bin/bash \n')
        f.write('#SBATCH --gres=gpu:1 \n')
        f.write('#SBATCH -o ' + slurm_out_dst + ' \n')
        f.write('module load singularity/3.5.2 \n')
        f.write(command_for_cellpose_with_dir)

    call_me = ['sbatch', '--job-name', rand_list[0], "--time", "0:05:00", "--mem-per-cpu", "5G", script_name]
    subprocess.call(call_me)
    #---------------------------------------------------------------------------


def expand_img(masked_file_path, tiff, dst):

    #Create and run resize script
    #---------------------------------------------------------------------------
    resize_script = os.path.join(os.getcwd(), 'segmentation/cellpose_segment/helpers/nucsmoothresize')
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


    #Case where num_z is 1
    #---------------------------------------------------------------------------
    if num_z == 1:
        num_z = 2
    #---------------------------------------------------------------------------

    #Stack 2d into 3d
    #---------------------------------------------------------------------------
    tiff_2d = tf.imread(src)
    print(f'{tiff_2d.shape=}')
    tiff_3d = []
    for z in range(num_z):
        tiff_3d.append(tiff_2d)
    tiff_3d = np.array(tiff_3d)
    #---------------------------------------------------------------------------

    #Save tif
    #---------------------------------------------------------------------------
    #tiff_3d = np.swapaxes(tiff_3d, 0, 2)
    print(f'{tiff_3d.shape=}')
    print('In get 3d from 2d')
    tf.imwrite(src, tiff_3d)
    #---------------------------------------------------------------------------


def get_labeled_img_cellpose(tiff_path, num_wav, nuclei_channel_num, dst=None, nuclei_radius=0, flow_threshold =.4, cell_prob_threshold=0, num_z = None):

    #Getting Tiff
    #----------------------------------------------
    print('Reading TIff')
    tiff = tiffy.load(tiff_path, num_wav, num_z)
    print(f'{tiff.shape=}')
    file_name = os.path.basename(tiff_path)
    dir_name = os.path.dirname(tiff_path)
    #----------------------------------------------

    #Shrink and save tif
    #---------------------------------------------------------------------------
    shrinked = get_shrinked(tiff, nuclei_channel_num)
    #shrinked.shape = [z,x,y]
    rand_list, rand_dir, dapi_tiff_dst = save_shrinked(shrinked)
    #---------------------------------------------------------------------------


    #Submit job and wait for it to finish
    #---------------------------------------------------------------------------
    num_z = len(shrinked)
    print(f'{num_z=}')
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


    print(f'{labeled_img.shape=}')

    #---------------------------------------------------------------------------

    shutil.rmtree(rand_dir)

    return labeled_img

if sys.argv[1] == 'debug_cellpose_low_z':
    labeled_img = get_labeled_img_cellpose(tiff_path = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3/segmentation/MMStack_Pos1.ome.tif',
                                            num_wav = 3,
                                            dst = '/home/nrezaee/temp/labeled_img_thresh_3.tif',
                                            nuclei_radius=20,
                                            nuclei_channel_num= -1,
                                            num_z = 1)
    print(f'{labeled_img.shape=}')

elif sys.argv[1] == 'debug_cellpose_michal':
    labeled_img = get_labeled_img_cellpose(tiff_path = '/groups/CaiLab/personal/Michal/raw/2021-06-21_Neuro4181_5_noGel_pool1/HybCycle_9/MMStack_Pos1.ome.tif',
                                            num_wav = 4,
                                            dst = '/home/nrezaee/temp/labeled_img_thresh_4.tif',
                                            nuclei_radius=20,
                                            nuclei_channel_num= -1,
                                            num_z = 1)
    print(f'{labeled_img.shape=}')


