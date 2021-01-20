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
import sys
import ast


sys.path.append(os.getcwd())


from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import plot_and_save_locations, get_visuals
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.dot_detectors_2d.dot_detector_2d import find_dots
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import apply_background_subtraction
from dot_detection.helpers.background_subtraction import get_background
from dot_detection.helpers.add_z import add_z_col
from dot_detection.helpers.threshold import apply_thresh
from dot_detection.helpers.compile_dots import add_to_dots_in_channel

warnings.filterwarnings("ignore")




def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, rand_dir):
    
    
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

    
    

        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    if channels_to_detect_dots=='all':
        
        channels = range(tiff.shape[1]-1)
    else:
        channels = [int(channel)-1 for channel in channels_to_detect_dots]
    
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]

        dots_in_channel = None

        
        #Loops through Z-stacks for Dot Detection
        #---------------------------------------------------------------------
        for z in range(tiff_shape[0]):
            
            tiff_2d = tiff_3d[z, :, :]
            
            #Background Subtraction
            #---------------------------------------------------------------------
            if bool_background_subtraction == True:
                tiff_2d = apply_background_subtraction(background, tiff_2d, z, channel)
            #---------------------------------------------------------------------
            

            #Normalize tiff 2d
            #---------------------------------------------------------------------
            tiff_2d = cv2.normalize(tiff_2d,  None, 0, 1000, cv2.NORM_MINMAX)
            #---------------------------------------------------------------------
            
            #Get dots from 2d image
            #---------------------------------------------------------------------
            dot_analysis = list(find_dots(tiff_2d))
            #---------------------------------------------------------------------
            
            #Add Z column to dot locations
            #---------------------------------------------------------------------
            dot_analysis = add_z_col(dot_analysis, z)
            #---------------------------------------------------------------------
            

            #Apply 1000 threshold
            #---------------------------------------------------------------------
            amount_of_dots_you_want_in_each_image = 20
            number_of_dots = len(dot_analysis[1])
            
            if number_of_dots < amount_of_dots_you_want_in_each_image:
                
                pass
            
            else:
                
                percentile = 100 - (amount_of_dots_you_want_in_each_image/number_of_dots)*100
                
                threshold = np.percentile(dot_analysis[1], percentile)
                
                dot_analysis = apply_thresh(dot_analysis, threshold)
            #---------------------------------------------------------------------


            #Switch [y, x, z] to [x, y, z]
            #---------------------------------------------------------------------
            dot_analysis[0][:,[0,1]] = dot_analysis[0][:,[1,0]]
            #---------------------------------------------------------------------
            
            
            
            #Shift Locations
            #---------------------------------------------------------------------
            dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
            #---------------------------------------------------------------------
            #print(f'{dot_analysis[0].shape=}')
  
            #Visualize Dots
            #---------------------------------------------------------------------
            median_z = tiff.shape[0]//2
            if bool_visualize_dots == True and channel == 1 and z == median_z:
                get_visuals(tiff_src, dot_analysis, tiff_2d)
            #---------------------------------------------------------------------

            #Add to dots in one z slace to dots in channel
            #---------------------------------------------------------------------
            dots_in_channel = add_to_dots_in_channel(dots_in_channel, dot_analysis)
            #---------------------------------------------------------------------

        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        assert dots_in_channel != None
        dots_in_tiff.append(dots_in_channel)
        
        
                
        import pickle
        with open(rand_dir+'/locs.pkl', 'wb') as f:
            pickle.dump(dots_in_tiff, f)
    
    #---------------------------------------------------------------------
    #-----------------------------------------------------------------
     
  
  
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--tiff_src")
parser.add_argument("--offset0")
parser.add_argument("--offset1")
parser.add_argument("--offset2")
parser.add_argument("--analysis_name")
parser.add_argument("--vis_dots")
parser.add_argument("--norm")
parser.add_argument("--back_subtract")
parser.add_argument("--channels", nargs = '+')
parser.add_argument("--chromatic")
parser.add_argument("--rand")


args, unknown = parser.parse_known_args()


if args.offset2 == 'None':
    offset = [float(args.offset0), float(args.offset1)]
else:    
    offset = [float(args.offset0), float(args.offset1), float(args.offset2)]


if args.channels[0] == 'all':
    channels = 'all'
else:
    channels = [int(i.replace('[', '').replace(']','').replace(',','')) for i in args.channels]



get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, args.vis_dots, args.norm, \
                      args.back_subtract, channels, args.chromatic, args.rand)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
