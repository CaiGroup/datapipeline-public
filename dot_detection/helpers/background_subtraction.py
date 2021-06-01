import cv2
import os
import glob
import sys
import tifffile as tf
import numpy as np

def apply_background_subtraction(background, tiff_2d, z, channel):
    background_2d = background[z, channel,:,:]
    tiff_2d = cv2.subtract(tiff_2d, background_2d)
    
    print("Running Background Subtraction")

    return tiff_2d

def get_background(tiff_src):
    tiff_split = tiff_src.split(os.sep)
    tiff_split[-2] = 'final_background'
    background_src = (os.sep).join(tiff_split)
    
    return background_src

def get_back_sub_check(tiff_src, analysis_name, back_img_3d):
    
    """
    Creates a check for background subtraction
    """
    
    #Split Tiff src
    #------------------------------------------------
    all_analyses_dir = '/groups/CaiLab/analyses'
    
    splitted_tiff_src = tiff_src.split(os.sep)
    personal = splitted_tiff_src[4]
    exp_name = splitted_tiff_src[6]
    hyb = splitted_tiff_src[-2]
    pos = tiff_src.split(os.sep)[-1].split('.ome')[0]
    #------------------------------------------------
    
    #Get destination for back sub check
    #------------------------------------------------
    pos_analysis_dir = os.path.join(all_analyses_dir, personal, exp_name, analysis_name, pos)
    back_sub_dir = os.path.join(pos_analysis_dir, 'Back_Sub_Check')
    os.makedirs(back_sub_dir, exist_ok= True)
    back_sub_dst = os.path.join(back_sub_dir, hyb + '.png')
    print(f'{back_sub_dst=}')
    #------------------------------------------------

    #Get and save middle z of back_sub
    #------------------------------------------------
    middle_z = back_img_3d.shape[0]//2
    tf.imwrite(back_sub_dst, np.log(back_img_3d[middle_z]))
    #------------------------------------------------
    
if sys.argv[1] == 'debug_back_sub_check':
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_1/MMStack_Pos0.ome.tif'
    analysis_name = 'linus_decoding'

    back_img_3d = tf.imread(tiff_src)[:, 0]
    
    get_back_sub_check(tiff_src, analysis_name, back_img_3d)
    