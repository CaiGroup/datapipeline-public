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
import pandas as pd



sys.path.append(os.getcwd())


from ...load_tiff import tiffy
from ..helpers.visualize_dots import plot_and_save_locations, get_visuals_3d
from ..reorder_hybs import get_and_sort_hybs
from ..dot_detectors_2d.dot_detector_2d import find_dots
from ..helpers.shift_locations import shift_locations
from ..helpers.background_subtraction import apply_background_subtraction
from ..helpers.background_subtraction import get_background
from ..helpers.add_z import add_z_col
from ..helpers.threshold import apply_thresh
from ..helpers.compile_dots import add_to_dots_in_channel

warnings.filterwarnings("ignore")

from ..gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from ..radial_center.radial_center_fitting import get_radial_centered_dots


def add_hyb_and_ch_to_df(dots_in_channel, tiff_src, channel):

    channel_array = np.full((len(dots_in_channel[1])), channel + 1)
    
    hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
    
    hyb_array = np.full((len(dots_in_channel[1])), hyb)

    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['hyb'] = hyb_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['hyb', 'ch', 'x','y','z','int'])

    return df

def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, n_dots, \
                      num_wav, rand_dir, num_z, bool_stack_z_dots):
    
    
    #Getting Background Src
    #--------------------------------------------------------------------
    if bool_background_subtraction == True:
        background_src = get_background(tiff_src)
        print(f'{background_src=}')
        background = tiffy.load(background_src, num_wav)
    #--------------------------------------------------------------------
    
    #Reading Tiff File
    #--------------------------------------------------------------------
    tiff = tiffy.load(tiff_src, num_wav, num_z)
    #--------------------------------------------------------------------
    

    #Set Basic Variables
    #---------------------------------------------------------------------
    dots_in_tiff = []
    
    tiff_shape = tiff.shape
    #---------------------------------------------------------------------

    df_tiff = pd.DataFrame(columns = ['hyb','ch', 'x', 'y', 'z', 'int'])

        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    if channels_to_detect_dots=='all':
        
        channels = range(tiff.shape[1]-1)
    else:
        channels = [int(channel)-1 for channel in channels_to_detect_dots]
    
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]

        dots_in_channel = None

        if bool_background_subtraction == True:
            print(f'{background.shape=}')
            print(f'{channel=}')
            tiff_3d = tiff_3d- background[:, channel]*.9
            
            tiff_3d = np.where(tiff_3d < 0, 0, tiff_3d)
        
        #Loops through Z-stacks for Dot Detection
        #---------------------------------------------------------------------
        for z in range(tiff_shape[0]):
            
            tiff_2d = tiff_3d[z, :, :]
            
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
            amount_of_dots_you_want_in_each_image = n_dots
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
            
  
            #Visualize Dots
            #---------------------------------------------------------------------
            print(f'{bool_visualize_dots=}')
            median_z = tiff.shape[0]//2
            if bool_visualize_dots == True and z == median_z:
                get_visuals_3d(tiff_src, dot_analysis, tiff_2d, analysis_name, z)
            #---------------------------------------------------------------------

            #Shift Locations
            #---------------------------------------------------------------------
            dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
            #---------------------------------------------------------------------
            
            
            #Add to dots in one z slace to dots in channel
            #---------------------------------------------------------------------
            dots_in_channel = add_to_dots_in_channel(dots_in_channel, dot_analysis)
            #---------------------------------------------------------------------

        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        assert dots_in_channel != None

        df_ch = add_hyb_and_ch_to_df(dots_in_channel, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        
    #Stack z dots
    #----------------------------------------------------------
    if bool_stack_z_dots:
        df_tiff.z = 1 
    #----------------------------------------------------------
    
    #Save to csv
    #----------------------------------------------------------
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)
    #----------------------------------------------------------

  
print(f'{sys.argv[1]=}')
if sys.argv[1] != 'debug_top_dots':
    print('Running')
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
    parser.add_argument("--norm")
    parser.add_argument("--back_subtract")
    parser.add_argument("--channels", nargs = '+')
    parser.add_argument("--chromatic")
    parser.add_argument("--n_dots")
    parser.add_argument("--rand")
    parser.add_argument("--num_wav")
    parser.add_argument("--num_z")
    parser.add_argument("--stack_z_s")
    
    
    args, unknown = parser.parse_known_args()
    
    
    if args.offset2 == 'None':
        offset = [float(args.offset0), float(args.offset1)]
    else:    
        offset = [float(args.offset0), float(args.offset1), float(args.offset2)]
    
    
    if args.channels[0] == 'all':
        channels = 'all'
    else:
        channels = [int(i.replace('[', '').replace(']','').replace(',','')) for i in args.channels]
    
    print(f'{args.stack_z_s=}')
    
    get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, str2bool(args.vis_dots), args.norm, \
                          str2bool(args.back_subtract), channels, args.chromatic, int(args.n_dots), args.num_wav, \
                          args.rand, args.num_z, str2bool(args.stack_z_s))
                          
else:                        
    print('Debugging')
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/simone_all/HybCycle_10/MMStack_Pos35.ome.tif'
    offset = [0,0,0]
    channels = 'all' #[1]
    analysis_name = 'back_sub'
    n_dots = 10
    rand_dir = '/home/nrezaee/temp'
    num_z = None
    back_sub = True
    num_dots = 10
    num_wav = 4
    visualize_dots = True
    get_dots_for_tiff(tiff_src, offset, analysis_name, visualize_dots, False, back_sub, channels, False, num_dots, num_wav, rand_dir, num_z)
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
