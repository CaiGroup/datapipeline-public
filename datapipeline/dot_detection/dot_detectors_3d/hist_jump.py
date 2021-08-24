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
import sys
import ast

from datapipeline.load_tiff import tiffy
from datapipeline.dot_detection.helpers.visualize_dots import plot_and_save_locations, get_visuals_3d
from datapipeline.dot_detection.reorder_hybs import get_and_sort_hybs
from datapipeline.dot_detection.helpers.shift_locations import shift_locations
from datapipeline.dot_detection.helpers.background_subtraction import apply_background_subtraction
from datapipeline.dot_detection.helpers.background_subtraction import get_background
from datapipeline.dot_detection.helpers.add_z import add_z_col
from datapipeline.dot_detection.helpers.threshold import apply_thresh
from datapipeline.dot_detection.helpers.compile_dots import add_to_dots_in_channel
from datapipeline.dot_detection.helpers.hist_jump_helpers import get_hist_threshed_dots
from datapipeline.dot_detection.helpers.remove_extra_dots import take_out_extra_dots

from datapipeline.dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from datapipeline.dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots


def run_back_sub(background, tiff_3d, channel, offset):
    print(4, flush=True)    
    background2d = scipy.ndimage.interpolation.shift(background[:,channel,:,:], np.negative(offset))[0,:,:]
    
    background3d = np.full((tiff_3d.shape[0], background2d.shape[0], background2d.shape[0]), background2d)

    tiff_3d = cv2.subtract(tiff_3d, background3d)
    tiff_3d[tiff_3d < 0] = 0

    
    return tiff_3d

warnings.filterwarnings("ignore")


def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, bool_gaussian_fitting, \
                      strictness, bool_radial_center, z_slices, num_wav, rand_dir):
    
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
        
        # n=7
        tiff_3d = tiff[:, channel,:,:]
        # print(f'{tiff_3d.shape=}')
        # tiff_3d = tiff_3d[:,n:tiff_3d.shape[1]-n,n:tiff.shape[2]-n]
        # print(f'{tiff_3d.shape=}')
        
        #Background Subtraction
        #---------------------------------------------------------------------
        if bool_background_subtraction == True:
            tiff_3d = run_back_sub(background, tiff_3d, channel, offset)
        #---------------------------------------------------------------------

        print((channel+1), end = " ", flush =True)
        
        #Check if 2d Dot Detection
        #---------------------------------------------------------------------
        if z_slices == 'all':
            pass
        
        else:
            tiff_3d= np.array([tiff_3d[z_slices,:,:]])
        #---------------------------------------------------------------------
        
        
        #Threshold on Biggest Jump
        #---------------------------------------------------------------------
        #strictness = 5
        print(f'{strictness=}')
        print(f'{tiff_3d.shape=}')
        dot_analysis = list(get_hist_threshed_dots(tiff_3d, strictness=strictness))
        # dot_analysis[0][:,0]+=n
        # dot_analysis[0][:,1]+=n
        
        print(f'{len(dot_analysis[1])=}')

        assert len(dot_analysis[1]) >0
        #---------------------------------------------------------------------
        
        
        #Gaussian Fit the dots
        #---------------------------------------------------------------------
        print(f'{bool_gaussian_fitting=}')
        if bool_gaussian_fitting == True:
            dot_analysis = get_gaussian_fitted_dots(tiff_src, channel, dot_analysis[0])
        #---------------------------------------------------------------------
        
        #Center the dots
        #---------------------------------------------------------------------
        print(f'{bool_radial_center=}')
        if bool_radial_center == True:
            dot_analysis = get_radial_centered_dots(tiff_src, channel, dot_analysis[0])
        #---------------------------------------------------------------------
        

        #Visualize Dots
        #---------------------------------------------------------------------
        median_z = tiff.shape[0]//2
        print(f'{bool_visualize_dots=}')
        if bool_visualize_dots == True:# and channel == 1 and z == median_z:
            get_visuals_3d(tiff_src, dot_analysis, tiff_3d[median_z], analysis_name)
        #---------------------------------------------------------------------
        
        
        #Shift Locations
        #---------------------------------------------------------------------
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
        #---------------------------------------------------------------------
        
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        dots_in_tiff.append(dot_analysis)
        print(f'{len(dots_in_tiff)=}')
        #---------------------------------------------------------------------
        import pickle
        with open(rand_dir+'/locs.pkl', 'wb') as f:
            pickle.dump(dots_in_tiff, f)
     #-----------------------------------------------------------------

     
def str2bool(v):
  return v.lower() == "true"

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--tiff_src")
parser.add_argument("--offset0")
parser.add_argument("--offset1")
parser.add_argument("--offset2")
parser.add_argument("--analysis_name")
parser.add_argument("--vis_dots")
parser.add_argument("--back_subtract")
parser.add_argument("--channels", nargs = '+')
parser.add_argument("--chromatic")
parser.add_argument("--rand")
parser.add_argument("--gaussian")
parser.add_argument("--radial_center")
parser.add_argument("--strictness")
parser.add_argument("--z_slices")
parser.add_argument("--z_slices")


args, unknown = parser.parse_known_args()

#print(f'{args.offset=}')

print(f'{args=}')

if args.offset2 == 'None':
    offset = [float(args.offset0), float(args.offset1)]
else:    
    offset = [float(args.offset0), float(args.offset1), float(args.offset2)]


if args.channels[0] == 'all':
    channels = 'all'
else:
    channels = [int(i.replace('[', '').replace(']','').replace(',','')) for i in args.channels]
    
if args.z_slices != 'all':
    args.z_slices = int(args.z_slices)

print(f'{args.gaussian=}')
print(f'{str2bool(args.gaussian)=}')
print(f'{args.radial_center=}')
print(f'{str2bool(args.radial_center)=}')


get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, str2bool(args.vis_dots), \
                      args.back_subtract, channels, args.chromatic, str2bool(args.gaussian), int(args.strictness), \
                      str2bool(args.radial_center), args.z_slices, args.num_wav, args.rand)
                      
                    #   tiff_src, offset, analysis_name, bool_visualize_dots, \
                    #   bool_background_subtraction, channels_to_detect_dots, bool_chromatic, bool_gaussian_fitting, \
                    #   strictness, bool_radial_center, z_slices, rand_dir):
    