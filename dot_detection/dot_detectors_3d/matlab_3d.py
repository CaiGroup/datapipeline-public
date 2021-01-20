from __future__ import annotations
import numpy as np
import imageio
import skimage
import tifffile
import os
import glob
from typing import Tuple
import numpy as np
from scipy import ndimage
import scipy.ndimage
from skimage.exposure import rescale_intensity
from skimage.feature import blob_log
from skimage.filters import difference_of_gaussians
from scipy.ndimage._ni_support import _normalize_sequence
import scipy.ndimage as ndi
import cv2
import warnings
import json
import warnings
import math
import matplotlib.pyplot as plt
import tempfile
from scipy.io import loadmat

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import plot_and_save_locations, get_visuals
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import apply_background_subtraction
from dot_detection.helpers.background_subtraction import get_background
from dot_detection.helpers.add_z import add_z_col
from dot_detection.helpers.threshold import apply_thresh
from dot_detection.helpers.compile_dots import add_to_dots_in_channel
from dot_detection.helpers.hist_jump_helpers import get_hist_threshed_dots 
from dot_detection.helpers.remove_extra_dots import take_out_extra_dots
from dot_detection.dot_detectors_3d.matlab_dot_detection.matlab_dot_detector import get_matlab_detected_dots
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots


def run_back_sub(background, tiff_3d, channel, offset):
    print(4, flush=True)    
    background2d = scipy.ndimage.interpolation.shift(background[:,channel,:,:], np.negative(offset))[0,:,:]
    
    background3d = np.full((tiff_3d.shape[0], background2d.shape[0], background2d.shape[0]), background2d)

    tiff_3d = cv2.subtract(tiff_3d, background3d)
    tiff_3d[tiff_3d < 0] = 0

    
    return tiff_3d

warnings.filterwarnings("ignore")


def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, bool_gaussian_fitting, strictness, z_slices, return_dict):
    
    #Getting Background Src
    #--------------------------------------------------------------------
    if bool_background_subtraction == True:
            background = get_background(tiff_src)
    #--------------------------------------------------------------------
    
    #Reading Tiff File
    #--------------------------------------------------------------------
    tiff = tiffy.load(tiff_src)
    #--------------------------------------------------------------------
    

    #Set Basic Variables
    #---------------------------------------------------------------------
    dots_in_tiff = []
    
    tiff_shape = tiff.shape
    #---------------------------------------------------------------------


    
    print("        Running on Channel:", end = " ", flush=True)
        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    if channels_to_detect_dots=='all':
        
        channels = range(tiff.shape[1]-1)
    else:
        channels = [int(channel)-1 for channel in channels_to_detect_dots]
    
    
    for channel in channels:
        
        dots_in_channel = None
        tiff_3d = tiff[:, channel,:,:]

        print((channel+1), end = " ", flush =True)
        
        #Check if 2d Dot Detection
        #---------------------------------------------------------------------
    #     if z_slices == 'all':
    #         pass
        
    #     else:
    #   #      tiff_3d= np.array([tiff_3d[z_slices,:,:]])
        #---------------------------------------------------------------------
        
        
        #Threshold on Biggest Jump for matlab 3d
        #---------------------------------------------------------------------
        #strictness = 5
        print(f'{strictness=}')
        print(f'{tiff_3d.shape=}')
        dot_analysis = get_matlab_detected_dots(tiff_src, channel, strictness)
        
        print(f'{len(dot_analysis[1])=}')

        assert len(dot_analysis[1]) >0
        #---------------------------------------------------------------------
        
        
        #Gaussian Fit the dots
        #---------------------------------------------------------------------
        #print(f'{bool_gaussian_fitting=}')
        if bool_gaussian_fitting == True:
            print('-------------------------------------------')
            dot_analysis = get_gaussian_fitted_dots(tiff_src, channel, dot_analysis[0])
            print('11111111111111111111111111111111')
        #---------------------------------------------------------------------
        
        #Shift Locations
        #---------------------------------------------------------------------
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
        #---------------------------------------------------------------------
        
        #Remove Extra Dots Across Z slices
        #---------------------------------------------------------------------
        if z_slices == 'all':
            dot_analysis = take_out_extra_dots(dot_analysis)
        #---------------------------------------------------------------------
        print("After taking out dots")
        print(f'{len(dot_analysis[0])=}')
        
        #Visualize Dots
        #---------------------------------------------------------------------
        median_z = tiff.shape[0]//2
        if bool_visualize_dots == True:# and channel == 1 and z == median_z:
            get_visuals(tiff_src, dot_analysis, tiff_3d[median_z], analysis_name)
        #---------------------------------------------------------------------
        
        #Convert to type objects
        #---------------------------------------------------------------------
        # dot_analysis[0] = dot_analysis[0].tolist()
        # dot_analysis[1] = dot_analysis[1].tolist()
        #---------------------------------------------------------------------
        
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        dots_in_tiff.append(dot_analysis)
        print(f'{len(dots_in_tiff)=}')
        #---------------------------------------------------------------------
        
     #-----------------------------------------------------------------

     
    print("")
    return_dict[tiff_src] = dots_in_tiff
    #return dots_in_tiff

