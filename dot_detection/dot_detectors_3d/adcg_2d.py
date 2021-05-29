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
import shutil



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
from helpers.rand_list import get_random_list

warnings.filterwarnings("ignore")

from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots


def add_hyb_and_ch_to_df(dots_in_channel, tiff_src, channel):

    #Get channel and hyb
    #-------------------------------------------------------------------
    channel_array = np.full((len(dots_in_channel[1])), channel + 1)
    hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
    hyb_array = np.full((len(dots_in_channel[1])), hyb)
    #-------------------------------------------------------------------
    
    #Set channel and hyb
    #-------------------------------------------------------------------
    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['hyb'] = hyb_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['hyb', 'ch', 'x','y','z','int'])
    #-------------------------------------------------------------------
    
    return df

def get_adcg_dots(tiff_2d, min_weight, final_loss):
    
    #Set and Make rand dir
    #-------------------------------------------------------------------
    rand = get_random_list(1)[0]
    temp_dir = os.path.join('/groups/CaiLab/personal/nrezaee/temp/temp_adcg', rand)
    os.mkdir(temp_dir)
    #-------------------------------------------------------------------
    
    #Set and save paths
    #-------------------------------------------------------------------
    tiff_txt_path = os.path.join(temp_dir, 'tiff_2d.txt')
    locs_result_path = os.path.join(temp_dir, 'locs.csv')
    output_path = os.path.join(temp_dir, 'adcg_output.out')
    np.savetxt(tiff_txt_path, tiff_2d)
    #-------------------------------------------------------------------
    
    #Set and run cmd
    #-------------------------------------------------------------------
    adcg_wrap_path = os.path.join(os.getcwd(), 'dot_detection/dot_detectors_3d/adcg', 'adcg_wrapper.sh')
    cmd = 'sbatch --wait ' + '--output ' + str(output_path)  + ' ' + adcg_wrap_path + ' ' + tiff_txt_path  \ 
        + ' ' + locs_result_path + ' ' + min_weight + ' ' + final_loss
    print(f'{cmd=}')
    os.system(cmd)
    #-------------------------------------------------------------------
    
    #Read Dataframe 
    #-------------------------------------------------------------------
    df_points = pd.read_csv(locs_result_path)
    #-------------------------------------------------------------------
    
    #Remove temp directory
    #-------------------------------------------------------------------
    shutil.rmtree(temp_dir)
    #-------------------------------------------------------------------
    
    return df_points
    
    
def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, num_wav, \
                      z_slices, rand_dir, min_weight, final_loss):
    
    
    #Getting Background Src
    #--------------------------------------------------------------------
    if bool_background_subtraction == True:
            background = get_background(tiff_src)
    #--------------------------------------------------------------------
    
    #Reading Tiff File
    #--------------------------------------------------------------------
    tiff = tiffy.load(tiff_src, num_wav)
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
    #-------------------------------------------------------------------
    
    #Loop through channels
    #-------------------------------------------------------------------
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]
        dots_in_channel = None

        print(f'{tiff_3d.shape=}')
        
        #Get Right z slices
        #-------------------------------------------------------------------
        if z_slices == 'all':
            pass
        
        else:
            print(f'{z_slices=}')
            print(f'{tiff_3d[z_slices,:,:].shape=}')
            tiff_3d= np.array([tiff_3d[z_slices,:,:]])
        #-------------------------------------------------------------------
            

        
        #Loops through Z-stacks for Dot Detection
        #---------------------------------------------------------------------
        df_points_3d = pd.DataFrame(columns = ['x', 'y', 'z', 'int'])
        for z in range(tiff_3d.shape[0]):
            tiff_2d = tiff_3d[z, :, :]
            
            #Run adcg on 2d slice
            #-------------------------------------------------------------------
            df_points_2d = get_adcg_dots(tiff_2d, min_weight)
            #-------------------------------------------------------------------
            
            #Change weight to intensity
            #-------------------------------------------------------------------
            df_points_2d = df_points_2d.rename(columns={'w': 'int'})
            df_points_2d['int'] = df_points_2d['int']/1000
            #-------------------------------------------------------------------
            
            #Set z column
            #-------------------------------------------------------------------
            z_array = np.full((df_points_2d.shape[0]), z)
            df_points_2d['z'] = z_array
            #-------------------------------------------------------------------
            
            #Show dots on png
            #-------------------------------------------------------------------
            if bool_visualize_dots == True and z == tiff_shape[0]//2:
                get_visuals(tiff_src, df_points_2d, tiff_2d, analysis_name)
            #-------------------------------------------------------------------
            
            #Add 2d points to 3d dataframe
            #-------------------------------------------------------------------
            df_points_3d = df_points_3d.append(df_points_2d)
            #-------------------------------------------------------------------
            
        
        #Get channel and hyb arrays
        #-------------------------------------------------------------------
        channel_array = np.full((df_points_3d.shape[0]), channel + 1)
        hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
        hyb_array = np.full((df_points_3d.shape[0]), hyb)
        #-------------------------------------------------------------------
        
        #Put channel and hyb in dataframe
        #-------------------------------------------------------------------
        df_points_3d['ch'] = channel_array
        df_points_3d['hyb'] = hyb_array
        #-------------------------------------------------------------------
        
        #Add points 3d to tiff with all channels
        #-------------------------------------------------------------------
        df_tiff = df_tiff.append(df_points_3d)
        #-------------------------------------------------------------------
        
        #Add offset to x and y
        #-------------------------------------------------------------------
        if offset != [0,0,0]:
            print('Shitfing Locations')
            df_tiff['x'] = df_tiff['x'] + offset[1]
            df_tiff['y'] = df_tiff['y'] + offset[0]
        #-------------------------------------------------------------------
        
    #Save to path
    #-------------------------------------------------------------------
    csv_path = os.path.join(rand_dir, 'locs.csv')
    df_tiff.to_csv(csv_path, index=False)
    #-------------------------------------------------------------------
  
print(f'{sys.argv[1]=}')
if sys.argv[1] != 'debug_adcg':
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
    parser.add_argument("--rand")
    parser.add_argument("--z_slices")
    parser.add_argument("--num_wav")
    parser.add_argument("--min_weight_adcg")
    parser.add_argument("--final_loss_adcg")
    
    
    
    args, unknown = parser.parse_known_args()
    
    
    if args.offset2 == 'None':
        offset = [float(args.offset0), float(args.offset1)]
    else:    
        offset = [float(args.offset0), float(args.offset1), float(args.offset2)]
    
    
    if args.channels[0] == 'all':
        channels = 'all'
    else:
        channels = [int(i.replace('[', '').replace(']','').replace(',','')) for i in args.channels]
    
    
    print(f'{args.z_slices=}')
    get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, str2bool(args.vis_dots), args.norm, \
                          args.back_subtract, channels, args.chromatic, args.num_wav, args.z_slices, 
                          args.rand, args.min_weight_adcg, args.final_loss_adcg)
                          
else:                        
    print('Debugging')
    get_dots_for_tiff(tiff_src ='/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_11/MMStack_Pos0.ome.tif', 
                        offset = [0,0],
                        analysis_name = 'linus_decoding', 
                        visualize_dots = True, 
                        bool_normalization = False, 
                        bool_background_subtraction = False, 
                        channels = [1], 
                        bool_chromatic = False, 
                        num_wav = 4, 
                        z_slice = 'all', 
                        rand_dir = '/tmp/nrezaee')
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
