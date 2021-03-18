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

    channel_array = np.full((len(dots_in_channel[1])), channel + 1)
    
    hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
    
    hyb_array = np.full((len(dots_in_channel[1])), hyb)

    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['hyb'] = hyb_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['hyb', 'ch', 'x','y','z','int'])

    return df

def get_adcg_dots(tiff_2d):
    
    rand = get_random_list(1)[0]
    
    temp_dir = os.path.join('/groups/CaiLab/personal/nrezaee/temp/temp_adcg', rand)
    os.mkdir(temp_dir)
    
    tiff_txt_path = os.path.join(temp_dir, 'tiff_2d.txt')
    locs_result_path = os.path.join(temp_dir, 'locs.csv')
    
    
    np.savetxt(tiff_txt_path, tiff_2d)
    
    adcg_wrap_path = os.path.join(os.getcwd(), 'dot_detection/dot_detectors_3d/adcg', 'adcg_wrapper.sh')
    
    cmd = 'sbatch --wait ' + adcg_wrap_path + ' ' + tiff_txt_path + ' ' + locs_result_path
    print(f'{cmd=}')
    
    os.system(cmd)
    
    df_points = pd.read_csv(locs_result_path)
    
    shutil.rmtree(temp_dir)
    
    return df_points
    
    
def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, num_wav, \
                      z_slices, rand_dir):
    
    
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
    
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]

        dots_in_channel = None
        
        print(f'{tiff_3d.shape=}')
        if z_slices == 'all':
            pass
        
        else:
            print(f'{z_slices=}')
            print(f'{tiff_3d[z_slices,:,:].shape=}')
            tiff_3d= np.array([tiff_3d[z_slices,:,:]])

            #tiff_3d = tiff_3d[np.newaxis, ...]

        
        #Loops through Z-stacks for Dot Detection
        #---------------------------------------------------------------------
        df_points_3d = pd.DataFrame(columns = ['x', 'y', 'z', 'int'])
        print(f'{tiff_3d.shape=}')
        for z in range(tiff_3d.shape[0]):
            
            tiff_2d = tiff_3d[z, :, :]
            
            df_points_2d = get_adcg_dots(tiff_2d)
            print(f'{df_points_2d=}')
            
            # del df_points_2d['int']
            
            df_points_2d = df_points_2d.rename(columns={'w': 'int'})
            df_points_2d['int'] = df_points_2d['int']/1000
            
            z_array = np.full((df_points_2d.shape[0]), z)
        
            df_points_2d['z'] = z_array
            
            if bool_visualize_dots == True and z == tiff_shape[0]//2:
                get_visuals(tiff_src, df_points_2d, tiff_2d, analysis_name)
            
            df_points_3d = df_points_3d.append(df_points_2d)
            
        
        channel_array = np.full((df_points_3d.shape[0]), channel + 1)
        hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
        hyb_array = np.full((df_points_3d.shape[0]), hyb)
        
        df_points_3d['ch'] = channel_array
        df_points_3d['hyb'] = hyb_array
        
        df_tiff = df_tiff.append(df_points_3d)
        print(f'{df_tiff.shape=}')
        
        if offset != [0,0,0]:
            print('Shitfing Locations')
            df_tiff['x'] = df_tiff['x'] + offset[1]
            df_tiff['y'] = df_tiff['y'] + offset[0]

        
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)

  
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
                          args.back_subtract, channels, args.chromatic, args.num_wav, args.z_slices, args.rand)
                          
else:                        
    print('Debugging')
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_5/MMStack_Pos0.ome.tif'
    offset = [1,1]
    channels = [1]
    analysis_name = 'linus_decoding'
    rand_dir = '/home/nrezaee/temp'
    visualize_dots = True
    z_slice = 0
    get_dots_for_tiff(tiff_src, offset, analysis_name, visualize_dots, False, False, channels, False, 4, z_slice, rand_dir)
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
