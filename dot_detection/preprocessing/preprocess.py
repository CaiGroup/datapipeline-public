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

        
def blur_3d(img_3d, kernel_size=5):
    
    print('Running Blur 3d with kernel size ' + str(kernel_size))
    
    blurred_img = np.zeros(img_3d.shape)
    
    #Loop through and blur 2d images
    #---------------------------------------------
    for i in range(len(img_3d)):
        blurred_img[i] = cv2.blur(img_3d[i], (int(kernel_size), int(kernel_size)))
    #---------------------------------------------
    
    return blurred_img
    
def blur_back_subtract(tiff_2d, kernel_size):
    """
    Blur the 2d img and then subtract it from itself
    """
    
    blur_kernel  = (int(kernel_size), int(kernel_size))
    blurry_img = cv2.blur(tiff_2d, blur_kernel)
    rolling_ball_subtracted_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return rolling_ball_subtracted_2d

def blur_back_subtract_3d(img_3d, kernel_size=1000):
    """
    Blur the 3d img and then subtract it from itself
    """
    
    print('Running Rolling Ball Subtraction with kernel size ' + str(kernel_size))
    
    rolling_ball_img = np.zeros(img_3d.shape)
    
    #Loop through and run rolling ball subtraction
    #---------------------------------------------
    for i in range(img_3d.shape[0]):
        rolling_ball_img[i,:,:] = blur_back_subtract(img_3d[i,:,:], kernel_size)
    #---------------------------------------------
    
    return rolling_ball_img

def normalize(img, max_norm=1000):
    """
    Normalize the img
    """
    norm_image = cv2.normalize(img, None, alpha=0, beta=max_norm, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return norm_image

def tophat_2d(img_2d, kernel_size):
    """
    Run tophat processing on a 2d img
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(int(kernel_size), int(kernel_size)))
    tophat_img = cv2.morphologyEx(img_2d, cv2.MORPH_TOPHAT, kernel)
    return tophat_img

def tophat_3d(img_3d, kernel_size = 200):
    """
    Run tophat processing on a 3d img
    """
    
    print('Running Tophat with kernel size ' + str(kernel_size))
    
    tophat_img_3d = np.zeros(img_3d.shape)
    for i in range(len(img_3d)):
        tophat_img_3d[i] = tophat_2d(img_3d[i], kernel_size)
    return tophat_img_3d

def preprocess_img(img_3d):
    """
    Run Preprocessing on a 3d img
    """

    #img_3d = blur_back_subtract_3d(img_3d)
    print(f'{img_3d.shape=}')
    img_3d = tophat_3d(img_3d)
    nonzero_img_3d = np.where(img_3d < 0, 0, img_3d)
    return nonzero_img_3d
    
def get_preprocess_check(tiff_src, analysis_name, preprocess_3d, channel, dir_check_name):
    
    """
    Creates a check for every step
    """
    
    #Only save preprocess check if there is analysis name
    if analysis_name != None:
        
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
        preprocess_dir = os.path.join(pos_analysis_dir, dir_check_name)
        os.makedirs(preprocess_dir, exist_ok= True)
        preprocess_dst = os.path.join(preprocess_dir, hyb + '_channel_' + str(channel) + '.png')
        print(f'{preprocess_dst=}')
        #------------------------------------------------
    
        #Normalize between 0 - 255
        #------------------------------------------------
        middle_z = preprocess_3d.shape[0]//2
        preprocess_2d = preprocess_3d[middle_z]
        
        preprocess_2d_log = np.log(preprocess_2d)
        preprocess_2d_log = np.where(preprocess_2d_log == -np.inf, 0, preprocess_2d_log)
        preprocess_2d_log = np.where(preprocess_2d_log == np.inf, 0, preprocess_2d_log)
        
        preprocess_norm_2d = (preprocess_2d_log/np.max(preprocess_2d_log))*255
        #------------------------------------------------
    
        #Get and save middle z of back_sub
        #------------------------------------------------
        io.imwrite(preprocess_dst, preprocess_norm_2d.astype(np.uint8))
        print('Saved PreProcess Check')
        #------------------------------------------------
    
    