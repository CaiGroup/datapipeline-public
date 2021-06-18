import cv2
import os
import glob
import json
import sys
import cv2
import tifffile as tf
import numpy as np
from scipy.ndimage import shift
import imageio as io

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
    io.imwrite(back_sub_dst, back_img_3d[middle_z].astype(np.uint8))
    print('Saved Back Sub Check')
    #------------------------------------------------
    
if sys.argv[1] == 'debug_back_sub_check':
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_1/MMStack_Pos0.ome.tif'
    analysis_name = 'linus_decoding'

    back_img_3d = tf.imread(tiff_src)[:, 0]
    
    get_back_sub_check(tiff_src, analysis_name, back_img_3d)
    
    
def shift_each_2d_in_3d(back_3d, offset):
    
    for i in range(len(back_3d)): 
        back_3d[i] = shift(back_3d[i], offset)
        
    return back_3d
    
def get_shifted_background(back_3d, tiff_src, analysis_name):
    """
    Get offset src and shift background
    """

    #Get offsets_src
    #-------------------------------------------------------------
    splitted_tiff_src = (tiff_src).split(os.sep)
    personal = splitted_tiff_src[4]
    exp_name = splitted_tiff_src[6]
    hyb = splitted_tiff_src[7]
    pos_with_ome = splitted_tiff_src[-1]
    pos = splitted_tiff_src[-1].split('.ome')[0]
    
    offsets_src = os.path.join('/groups/CaiLab/analyses', personal, exp_name, analysis_name, pos, 'offsets.json')
    print(f'{offsets_src=}')
    #-------------------------------------------------------------
    
    #Read in offset
    #-------------------------------------------------------------
    with open(offsets_src) as f:
        offsets = json.load(f)
    #-------------------------------------------------------------
    
    #Get background offset 
    #-------------------------------------------------------------
    back_offset_keys = [offset_key for offset_key in offsets.keys() if 'final_background' in offset_key]
    assert len(back_offset_keys) == 1, "There is more than or less than one background aligned in offsets"
    back_offset = np.array(offsets[back_offset_keys[0]])
    print(f'{back_offset=}')
    #-------------------------------------------------------------
    
    #Get hyb offset_key
    #-------------------------------------------------------------
    hyb_offset_key = hyb + '/' + splitted_tiff_src[-1]
    hyb_offset = np.array(offsets[hyb_offset_key])
    print(f'{hyb_offset=}')
    #-------------------------------------------------------------
    
    #Shift image
    #-------------------------------------------------------------
    print("Shifting Background")
    print(f'{back_3d.shape=}')
    hyb_minus_back_offset =  hyb_offset - back_offset
    print(f'{hyb_minus_back_offset=}')
    
    if len(back_offset) == 3:
        shifted_back = shift(back_3d, hyb_minus_back_offset)
    elif len(back_offset) == 2:
        shifted_back = shift_each_2d_in_3d(back_3d, hyb_minus_back_offset)
    #-------------------------------------------------------------
    
    return shifted_back

if sys.argv[1] == 'debug_shift_background':
    tiff_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_10/MMStack_Pos0.ome.tif'
    analysis_name = 'anthony_test_1'
    tiff = tf.imread(tiff_src)
    back_tiff = tiff[:,0]
    shifted_back = get_shifted_background(back_tiff, tiff_src, analysis_name)
    print(f'{shifted_back.shape=}')
    

    