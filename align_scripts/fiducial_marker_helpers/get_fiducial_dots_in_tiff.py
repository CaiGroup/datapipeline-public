import os 
import numpy as np
import warnings
import matplotlib.pyplot as plt
import pandas as pd

import sys
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from load_tiff import tiffy
import load_tiff

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

from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots


def add_ch_to_df(dots_in_channel, tiff_src, channel):

    channel_array = np.full((len(dots_in_channel[1])), channel + 1)

    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['ch', 'x','y','z','int'])

    return df

def get_fiducial_visual_debug(fid_tiff, fid_locs, dst):
    for channel in fid_locs.ch.unique():
        for i in range(fid_tiff[:, channel].shape[0]):
            locs_z = fid_locs[(fid_locs.z == i) & (fid_locs.ch == channel)]
            plt.figure(figsize=(10,10))
            plt.scatter(locs_z.x, locs_z.y)
            png_dst = os.path.join(dst, 'channel_' +str(channel) + '_z_' + str(i) + '.png')
            plt.imshow(np.log(fid_tiff[i, channel]), cmap='gray')
            print(f'{png_dst=}')
            plt.savefig(png_dst)
        

def get_dots_for_tiff(tiff_src, num_wav, dst, channels_to_detect_dots = 'all'):
    
    #Reading Tiff File
    #--------------------------------------------------------------------
    tiff = tiffy.load(tiff_src, num_wav)
    #--------------------------------------------------------------------
    

    #Set Basic Variables
    #---------------------------------------------------------------------
    dots_in_tiff = []
    
    tiff_shape = tiff.shape
    #---------------------------------------------------------------------

    
    df_tiff = pd.DataFrame(columns = ['ch', 'x', 'y', 'z', 'int'])

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
            amount_of_dots_you_want_in_each_image = 100
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
            dot_analysis[0][:,[2,0]] = dot_analysis[0][:,[0,2]]
            #---------------------------------------------------------------------
            
            
            #Add to dots in one z slice to dots in channel
            #---------------------------------------------------------------------
            dots_in_channel = add_to_dots_in_channel(dots_in_channel, dot_analysis)
            #---------------------------------------------------------------------

        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        assert dots_in_channel != None
        
        df_ch = add_ch_to_df(dots_in_channel, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        
    get_fiducial_visual_debug(tiff, df_tiff, dst='foo')
    
    print('df_tiff in dot detection ' + str(df_tiff))
    return df_tiff
    #---------------------------------------------------------------------
    
import sys
if sys.argv[1] == 'debug_fid_dot_detect':
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-10-19-takei/final_fiducials/MMStack_Pos0.ome.tif'
    
    dst = 'foo'
    num_wav = 4
    df_tiff = get_dots_for_tiff(tiff_src, 4, dst)
    print(f'{type(df_tiff)=}')
    print(f'{df_tiff=}')

    
    
     