import os 
import cv2
import numpy as np
import scipy.ndimage
import json
import glob
import sys
sys.path.insert(0, os.getcwd())
from load_tiff import tiffy
from align_scripts.mean_squares_blur import preprocess_align


main_dir = '/groups/CaiLab'

def crop_center(img,cropx,cropy):
    
    y,x = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)    
    return img[starty:starty+cropy,startx:startx+cropx]
    
def get_and_sort_hybs(path_to_experiment_dir):
    
    #Get all files in path
    #-------------------------------------------------
    hyb_dirs = glob.glob(path_to_experiment_dir)
    #-------------------------------------------------
    
    
    #Remove anything that is not a Hyb
    #-------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in hyb_dirs if 'Hyb' in hyb_dir]
    #-------------------------------------------------
    
    
    #Split hybs to get numbers
    #-------------------------------------------------
    split_word = 'Cycle_'
    for index in range(len(hyb_dirs)):

        hyb_dirs[index] = hyb_dirs[index].split(split_word)
 
        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    #-------------------------------------------------
    
    
    #Sort the Hybs
    #-------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    #-------------------------------------------------

    
    #Combine the strings to right format
    #-------------------------------------------------
    for index in range(len(sorted_hyb_dirs)):
        sorted_hyb_dirs[index][1] = str(sorted_hyb_dirs[index][1])
        sorted_hyb_dirs[index].insert(1, split_word)
        sorted_hyb_dirs[index] = ''.join(sorted_hyb_dirs[index])
    #-------------------------------------------------
    
    
    return sorted_hyb_dirs
    
    
#Gets the center of the moving and fixed image
#------------------------------------------------------------------------------
def get_moving_and_fixed_3d(fixed_tiff, moving_tiff):
    
    
    # fixed_dapi_img = preprocess_align(fixed_tiff[:,3,:,:])
    # moving_dapi_img = preprocess_align(moving_tiff[:,3,:,:])

    fixed_dapi_img = fixed_tiff[:,-1,:,:]
    moving_dapi_img = moving_tiff[:,-1,:,:]

    cropx = 1000
    cropy = 1000
    
    fixed_img_center = []
    moving_img_center = []
    
    start_z = fixed_tiff.shape[0]//4
    end_z = (fixed_tiff.shape[0]//4)*3
    #print("        Fixed Image Shape:", fixed_dapi_img.shape)
    for z_index in range(start_z, end_z):
        fixed_img_center.append(crop_center(fixed_dapi_img[z_index], cropx, cropy))
        moving_img_center.append(crop_center(moving_dapi_img[z_index], cropx, cropy))
        
    fixed_img_center = np.array(fixed_img_center)
    moving_img_center = np.array(moving_img_center)
    
    return moving_img_center, fixed_img_center 
#------------------------------------------------------------------------------

#Gets the center of the moving and fixed image
#------------------------------------------------------------------------------
def get_moving_and_fixed_2d(fixed_tiff, moving_tiff):
    
    
    # fixed_dapi_img = preprocess_align(fixed_tiff[:,3,:,:])
    # moving_dapi_img = preprocess_align(moving_tiff[:,3,:,:])

    fixed_dapi_img = fixed_tiff[:,-1,:,:]
    moving_dapi_img = moving_tiff[:,-1,:,:]

    cropx = 1000
    cropy = 1000
    
    
    median_z = (fixed_tiff.shape[0]//2)
    #print("        Fixed Image Shape:", fixed_dapi_img.shape)

    fixed_img_center = crop_center(fixed_dapi_img[median_z], cropx, cropy)
    moving_img_center = crop_center(moving_dapi_img[median_z], cropx, cropy)
        

    
    fixed_img_center = np.array(fixed_img_center)
    moving_img_center = np.array(moving_img_center)
    
    return moving_img_center, fixed_img_center 
#------------------------------------------------------------------------------





def get_shifted(fixed_tiff, moving_tiff, offset):
    
    # fixed_dapi_img = preprocess_align(fixed_tiff[:,3,:,:])
    # moving_dapi_img = preprocess_align(moving_tiff[:,3,:,:])

    fixed_dapi_img = fixed_tiff[:,-1,:,:]
    moving_dapi_img = moving_tiff[:,-1,:,:]
    
    
    shifted_dapi_img = scipy.ndimage.interpolation.shift(moving_dapi_img, offset)

    #assert np.sum(shifted_dapi_img) != 0
    
    shifted_dapi_img_center = []
    fixed_dapi_img_center = [] 

    start_z = fixed_tiff.shape[0]//4
    end_z = (fixed_tiff.shape[0]//4)*3
    #print("        Fixed Image Shape:", fixed_dapi_img.shape)
    for z_index in range(start_z, end_z):
        shifted_dapi_img_center.append(crop_center(shifted_dapi_img[z_index], 1000, 1000))
        fixed_dapi_img_center.append(crop_center(fixed_dapi_img[z_index], 1000, 1000))
        
    shifted_dapi_img_center_np = np.array(shifted_dapi_img_center)
    fixed_dapi_img_center_np = np.array(fixed_dapi_img_center)
        
    return shifted_dapi_img_center_np
    
def get_shifted_2d(fixed_tiff, moving_tiff, offset):
    
    # fixed_dapi_img = preprocess_align(fixed_tiff[:,3,:,:])
    # moving_dapi_img = preprocess_align(moving_tiff[:,3,:,:])

    fixed_dapi_img = fixed_tiff[:,-1,:,:]
    moving_dapi_img = moving_tiff[:,-1,:,:]
    
    median_z = moving_dapi_img.shape[0]//2
    
   # print(f)
    shifted_dapi_img = scipy.ndimage.interpolation.shift(moving_dapi_img[median_z], offset)
    
    assert np.sum(shifted_dapi_img) != 0
    
    shifted_dapi_img_center = []
    fixed_dapi_img_center = [] 

    shifted_dapi_img_center_np = np.array(crop_center(shifted_dapi_img, 1000, 1000))

    return shifted_dapi_img_center_np
#------------------------------------------------------------------------------


def get_align_errors(fixed_tiff, moving_tiff, offset):
    
    dims_to_align = len(offset)
    
    if dims_to_align ==3:
        moving_dapi_img_center_np, fixed_dapi_img_center_np  = get_moving_and_fixed_3d(fixed_tiff, \
                                                                                    moving_tiff)
        shifted_dapi_img_center_np = get_shifted(fixed_tiff, moving_tiff, offset)
        
    elif dims_to_align  == 2:
        moving_dapi_img_center_np, fixed_dapi_img_center_np  = get_moving_and_fixed_2d(fixed_tiff, \
                                                                                    moving_tiff)
        shifted_dapi_img_center_np = get_shifted_2d(fixed_tiff, moving_tiff, offset)
        
        
    former_diff = int(abs(np.sum(cv2.subtract(fixed_dapi_img_center_np, moving_dapi_img_center_np))))
    print("        Former Difference:", str(former_diff))
    new_diff = int(abs(np.sum(cv2.subtract(fixed_dapi_img_center_np, shifted_dapi_img_center_np))))
    print("        New diff:", str(new_diff))        
    
    if former_diff == 0:
        error = "No Difference 0% (Same as compared DAPI Image)"
    else:
        improv_percent = ((former_diff-new_diff)/former_diff)
        if improv_percent > 0:
            error = "Improved by "+"{:.2%}".format(improv_percent)
            #error = "Improved by " + str(improv_percent) 
        else:
            error = "Worsened by "+"{:.2%}".format(improv_percent)
            #error = "Worsened by " + str(improv_percent)
    
    print("Align Error:", str(error))
    return error

import sys
if sys.argv[1] == 'debug_align_errors':
    channel = 0
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/test1/HybCycle_1/MMStack_Pos0.ome.tif'
    tiff = tiffy.load(tiff_src, num_wav=4)
    tiff_ch = tiff[:,channel]

    get_align_errors(tiff, tiff, [0,20])
    
        



