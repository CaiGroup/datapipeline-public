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

def blur_back_subtract(tiff_2d, num_tiles):
    """
    Blur the 2d img and then subtract it from itself
    """
    
    blur_kernel  = tuple(np.array(tiff_2d.shape)//num_tiles)
    blurry_img = cv2.blur(tiff_2d,blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return tiff_2d

def blur_back_subtract_3d(img_3d, num_tiles=10):
    """
    Blur the 3d img and then subtract it from itself
    """
    
    for i in range(img_3d.shape[0]):
        img_3d[i,:,:] = blur_back_subtract(img_3d[i,:,:], num_tiles)
    return img_3d

def normalize(img, max_norm=1000):
    """
    Normalize the img
    """
    norm_image = cv2.normalize(img, None, alpha=0, beta=max_norm, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return norm_image

def tophat_2d(img_2d):
    """
    Run tophat processing on a 2d img
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(20,20))
    tophat_img = cv2.morphologyEx(img_2d, cv2.MORPH_TOPHAT, kernel)
    return tophat_img

def tophat_3d(img_3d):
    """
    Run tophat processing on a 3d img
    """
    print(f'{img_3d.shape=}')
    for i in range(len(img_3d)):
        print(f'{i=}')
        img_3d[i] = tophat_2d(img_3d[i])
    return img_3d

def preprocess_img(img_3d):
    """
    Run Preprocessing on a 3d img
    """

    blur_img_3d = blur_back_subtract_3d(img_3d)
    print(f'{blur_img_3d.shape=}')
    #tophat_img_3d = tophat_3d(blur_img_3d)
    nonzero_img_3d = np.where(blur_img_3d < 0, 0, blur_img_3d)
    return nonzero_img_3d
    
def get_preprocess_check(tiff_src, analysis_name, preprocess_3d, channel):
    
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
    preprocess_dir = os.path.join(pos_analysis_dir, 'PreProcess_Check')
    os.makedirs(preprocess_dir, exist_ok= True)
    preprocess_dst = os.path.join(preprocess_dir, hyb + '_channel_' + str(channel) + '.png')
    print(f'{preprocess_dst=}')
    #------------------------------------------------

    #Get and save middle z of back_sub
    #------------------------------------------------
    middle_z = preprocess_3d.shape[0]//2
    io.imwrite(preprocess_dst, preprocess_3d[middle_z].astype(np.uint8))
    print('Saved PreProcess Check')
    #------------------------------------------------
    
    