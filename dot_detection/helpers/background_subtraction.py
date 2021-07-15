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
sys.path.insert(0, os.getcwd())
from load_tiff import tiffy
from matplotlib import cm

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

def get_back_sub_check(tiff_src, analysis_name, back_img_3d, channel):
    
    """
    Creates a check for background subtraction
    """
    
    if 'ipykernel' not in sys.argv[0]:
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
        back_sub_dst = os.path.join(back_sub_dir, hyb + '_channel_' + str(channel) +'.png')
        print(f'{back_sub_dst=}')
        #------------------------------------------------
    
        #Get and save middle z of back_sub
        #------------------------------------------------
        middle_z = back_img_3d.shape[0]//2
        
        logged_img = np.log(back_img_3d[middle_z].astype(np.uint8))
        
        logged_img = np.where(logged_img == -np.inf, 0, logged_img)
        io.imwrite(back_sub_dst, logged_img)
        print('Saved Back Sub Check')
        #------------------------------------------------
    
if sys.argv[1] == 'debug_back_sub_check':
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_1/MMStack_Pos0.ome.tif'
    analysis_name = 'linus_decoding'
    channel = 0
    back_img_3d = tf.imread(tiff_src)[:, 0]
    
    get_back_sub_check(tiff_src, analysis_name, back_img_3d, channel)
    
    
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
    offset_back_minus_hyb = back_offset - hyb_offset
    print(f'{offset_back_minus_hyb=}')
    
    if len(back_offset) == 3:
        
        raise ValueError('The background subtraction for 3d needs to be double checked to see if the offset is aligning stuff correctly.')
        shifted_back = shift(back_3d, offset_back_minus_hyb)
        
    elif len(back_offset) == 2:
        shifted_back = shift_each_2d_in_3d(back_3d, offset_back_minus_hyb)
    #-------------------------------------------------------------
    
    return shifted_back

if sys.argv[1] == 'debug_shift_background':
    tiff_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_10/MMStack_Pos0.ome.tif'
    analysis_name = 'anthony_test_1'
    tiff = tf.imread(tiff_src)
    back_tiff = tiff[:,0]
    shifted_back = get_shifted_background(back_tiff, tiff_src, analysis_name)
    print(f'{shifted_back.shape=}')
    

def get_background_mask_2d(back_img_2d):
    
    #Blur Image
    #---------------------------------------------------
    img_blur = cv2.blur(back_img_2d, (10,10) ,cv2.BORDER_DEFAULT)
    #---------------------------------------------------
    
    #Log Image
    #---------------------------------------------------
    log_img_blur = np.log(img_blur)
    #---------------------------------------------------
    
    #Normalize Image
    #---------------------------------------------------
    norm_img_between_0_and_1 = log_img_blur/log_img_blur.max()
    norm_img = norm_img_between_0_and_1*255
    norm_img = norm_img.astype(np.uint8)
    #---------------------------------------------------
    
    #Threshold Image
    #---------------------------------------------------
    adaptive_image_thresh = cv2.adaptiveThreshold(norm_img,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY_INV,201,-10)
    #---------------------------------------------------
    
    #Change 255 to 1
    #---------------------------------------------------
    adaptive_image_thresh = np.where(adaptive_image_thresh == 255, 1, adaptive_image_thresh)
    #---------------------------------------------------
    
    return adaptive_image_thresh

def get_background_mask(back_tiff_3d):
    
    #Initalize result variable
    #---------------------------------------------------
    back_tiff_mask = np.zeros(back_tiff_3d.shape)
    #---------------------------------------------------
    
    #Loop through 3d background and get masks
    #---------------------------------------------------
    for z_i in range(back_tiff_3d.shape[0]):
        back_tiff_mask[z_i] = get_background_mask_2d(back_tiff_3d[z_i])
    #---------------------------------------------------
    
    return back_tiff_mask

def remove_blobs_with_masks_3d(back_tiff_ch, tiff_ch, tiff_src, analysis_name, channel):
    """
    Takes in a 3d Background and a 3d tiff 
    Then finds the blobs and removes them from the tiff
    """
    
    #Get back subtracted tiff
    #---------------------------------------------------
    back_tiff_ch_mask = get_background_mask(back_tiff_ch)
    #---------------------------------------------------
    
    #Remove blobs
    #---------------------------------------------------
    tiff_ch_blobs_removed = back_tiff_ch_mask*tiff_ch
    #---------------------------------------------------
    
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
    blob_removal_dir = os.path.join(pos_analysis_dir, 'Back_Blob_Removal_Check')
    os.makedirs(blob_removal_dir, exist_ok= True)
    blob_removal_dst = os.path.join(blob_removal_dir, hyb + '_channel_'+ str(channel) +'.png')
    print(f'{blob_removal_dst=}')
    #------------------------------------------------
    
    #Save tiff_ch_blobs_removed
    #------------------------------------------------
    tiff_ch_blobs_removed_middle_z = tiff_ch_blobs_removed[tiff_ch_blobs_removed.shape[0]//2]
    logged_tiff_ch_blobs_removed_middle_z = np.log(tiff_ch_blobs_removed_middle_z)
    logged_tiff_ch_blobs_removed_middle_z[logged_tiff_ch_blobs_removed_middle_z == -np.inf] = 0 
    io.imwrite(blob_removal_dst, logged_tiff_ch_blobs_removed_middle_z)
    #------------------------------------------------
    
    #Save Blobbed image
    #------------------------------------------------
    blob_mask_dst = os.path.join(blob_removal_dir, 'blob_mask_channel_' + str(channel) + '.png')
    print(f'{blob_mask_dst=}')
    back_tiff_ch_mask_middle_z = back_tiff_ch_mask[back_tiff_ch_mask.shape[0]//2]
    if not os.path.exists(blob_mask_dst):
        io.imwrite(blob_mask_dst, back_tiff_ch_mask_middle_z)
    #------------------------------------------------
    
    
    return tiff_ch_blobs_removed

if sys.argv[1] == 'debug_remove_back_blobs':
    analysis_name = 'anthony_test_1'
    tiff_src = '/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013/HybCycle_10/MMStack_Pos12.ome.tif'
    back_tiff = tiffy.load('/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013/final_background/MMStack_Pos12.ome.tif')
    tiff = tiffy.load(tiff_src)
    print(f'{back_tiff.shape=}')
    ch = 1
    back_tiff_ch = back_tiff[:, ch]
    tiff_ch = tiff[:, ch]
    remove_blobs_with_masks_3d(back_tiff_ch, tiff_ch, tiff_src, analysis_name, ch)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    