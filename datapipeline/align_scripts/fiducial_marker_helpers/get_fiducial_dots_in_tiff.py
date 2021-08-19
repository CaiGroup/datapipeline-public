import numpy as np
import tifffile as tf
import os
import warnings
import sys
import pandas as pd
import scipy 
import cv2
import matplotlib.pyplot as plt

from ...load_tiff import tiffy
from ...dot_detection.helpers.visualize_dots import get_visuals_3d
from ...dot_detection.helpers.shift_locations import shift_locations
from ...dot_detection.helpers.background_subtraction import get_background
from .fid_jump_helpers import hist_jump_threshed_3d
from ...dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from ...dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots

warnings.filterwarnings("ignore")


def get_fiducial_visual_debug(fid_tiff, fid_locs, dst):

    os.makedirs(dst, exist_ok = True)
    
    #Loop through and plot each fid for ch
    #------------------------------------------------------
    for channel in fid_locs.ch.unique():
        
        #Loop through each z
        #------------------------------------------------------
        for i in range(fid_tiff[:, channel-1].shape[0]):
            
            #Get locs for ch and z
            #------------------------------------------------------
            locs_z = fid_locs[(fid_locs.z == i) & (fid_locs.ch == channel)]
            #------------------------------------------------------
            
            #Plot dots on image
            #------------------------------------------------------
            plt.figure(figsize=(40,40))
            plt.imshow(np.log(fid_tiff[i, channel-1]), cmap='gray')
            plt.scatter(locs_z.x, locs_z.y, facecolors='none', edgecolors='y', s=2000)
            #------------------------------------------------------
            
            #Save plot
            #------------------------------------------------------
            png_dst = os.path.join(dst, 'channel_' +str(channel) + '_z_' + str(i) + '.png')
            plt.savefig(png_dst)
            #------------------------------------------------------

def add_ch_to_df(dots_in_channel, tiff_src, channel):
    
    #Get numpy array for channel columns
    #--------------------------------------------------------
    channel_array = np.full((len(dots_in_channel[1])), channel + 1)
    #--------------------------------------------------------
    
    #Set values in dataframe
    #--------------------------------------------------------
    df_tiff = pd.DataFrame(columns = ['ch', 'x', 'y', 'z', 'int'])
    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['int'] = dots_in_channel[1]
    #--------------------------------------------------------
    
    #Sort columns in ceratin way
    #--------------------------------------------------------
    df = df.reindex(columns=['ch', 'x','y','z','int'])
    #--------------------------------------------------------
    
    return df

def get_dots_for_tiff(tiff_src,num_wav, dst, dot_radius, strictness=-3):
    
    
    #Reading Tiff File
    #--------------------------------------------------------------------
    tiff = tiffy.load(tiff_src, num_wav)
    #--------------------------------------------------------------------
    

    #Set Basic Variables
    #---------------------------------------------------------------------
    dots_in_tiff = []
    tiff_shape = tiff.shape
    df_tiff = pd.DataFrame(columns = ['ch', 'x', 'y', 'z', 'int'])
    #---------------------------------------------------------------------


    #Loop through each channel
    #---------------------------------------------------------------------
    channels = range(tiff.shape[1]-1)
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]
    
        #Run Dot Detection
        #---------------------------------------------------------------------
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, dot_radius))
        assert len(dot_analysis[1]) >0
        #---------------------------------------------------------------------
        
        #Reorganize x,y,z
        #---------------------------------------------------------------------
        dot_analysis[0][:, [0,2]] = dot_analysis[0][:, [2,0]]
        #---------------------------------------------------------------------
    
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        df_ch = add_ch_to_df(dot_analysis, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        #---------------------------------------------------------------------
    
    #Get visual debug for fiducials
    #---------------------------------------------------------------------
    os.makedirs(dst, exist_ok = True)
    get_fiducial_visual_debug(tiff, df_tiff, dst)
    #---------------------------------------------------------------------
    
    #Save locs to destination
    #---------------------------------------------------------------------
    csv_path = os.path.join(dst,'locs.csv')
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)
    #---------------------------------------------------------------------
    
    return df_tiff
    
#Debug
#-----------------------------------------------------------------
import sys
if sys.argv[1] == 'debug_fid_dot_detect_takei':
    df_tiff = get_dots_for_tiff(tiff_src='/groups/CaiLab/personal/nrezaee/raw/2020-10-19-takei/initial_fiducials/MMStack_Pos0.ome.tif',
                                strictness=15, 
                                num_wav=4,
                                dot_radius=2,
                                dst='foo/final')
                                
    print(f'{type(df_tiff)=}')
    print(f'{df_tiff=}')


if sys.argv[1] == 'debug_fid_dot_detect_linus':
    df_tiff = get_dots_for_tiff(tiff_src='/groups/CaiLab/personal/nrezaee/raw/linus_data/initial_fiducials/MMStack_Pos0.ome.tif',
                                strictness=15, 
                                num_wav=4,
                                dot_radius=2,
                                dst='foo/linus_fid')
                                
    print(f'{type(df_tiff)=}')
    print(f'{df_tiff=}')

    
    
     