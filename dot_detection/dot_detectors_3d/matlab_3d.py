import numpy as np
import os
import glob
import numpy as np
import warnings
import pandas as pd
import cv2

import sys

sys.path.insert(0, os.getcwd())

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import get_visuals_3d
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import apply_background_subtraction
from dot_detection.helpers.background_subtraction import get_background, get_back_sub_check, get_shifted_background, remove_blobs_with_masks_3d
from dot_detection.helpers.add_z import add_z_col

from dot_detection.helpers.threshold import apply_thresh
from dot_detection.helpers.compile_dots import add_to_dots_in_channel
from dot_detection.helpers.hist_jump_helpers import get_hist_threshed_dots 
from dot_detection.helpers.remove_extra_dots import take_out_extra_dots
from dot_detection.dot_detectors_3d.matlab_dot_detection.matlab_dot_detector import get_matlab_detected_dots
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots

def run_back_sub(background, tiff_3d, channel, offset):
    print(4, flush=True)    
    background2d = scipy.ndimage.interpolation.shift(background[:,channel,:,:], np.negative(offset))[0,:,:]
    
    background3d = np.full((tiff_3d.shape[0], background2d.shape[0], background2d.shape[0]), background2d)

    tiff_3d = cv2.subtract(tiff_3d, background3d)
    tiff_3d[tiff_3d < 0] = 0

    
    return tiff_3d

warnings.filterwarnings("ignore")

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

def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, bool_gaussian_fitting, \
                      bool_radial_center, strictness, z_slices, nbins, threshold, num_wav, bool_stack_z_dots, 
                      bool_blob_removal, rand_dir):
    
    #Getting Background Src
    #--------------------------------------------------------------------
    if bool_background_subtraction == True or bool_blob_removal == True:
            background_src = get_background(tiff_src)
            print(f'{background_src=}')
            background = tiffy.load(background_src, num_wav)
            print(f'{background.shape=}')
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
        
        #Background Subtraction
        #---------------------------------------------------------------------
        if bool_background_subtraction == True:
            # tiff_3d = run_back_sub(background, tiff_3d, channel, offset)
            print(f'{background.shape=}')
            print(f'{channel=}')
            back_3d = get_shifted_background(background[:, channel], tiff_src, analysis_name)
            tiff_3d = cv2.subtract(tiff_3d, back_3d)
            get_back_sub_check(tiff_src, analysis_name, tiff_3d, channel)
        #---------------------------------------------------------------------
        
        
        #Background Blob Removal
        #---------------------------------------------------------------------
        if bool_blob_removal == True:
            tiff_3d = remove_blobs_with_masks_3d(background[:, channel], tiff_3d, tiff_src, analysis_name, channel)
        #---------------------------------------------------------------------
        
        print((channel+1), end = " ", flush =True)
        

        
        #Threshold on Biggest Jump for matlab 3d
        #---------------------------------------------------------------------
        #strictness = 5
        print(f'{strictness=}')
        print(f'{tiff_3d.shape=}')
        dot_analysis = get_matlab_detected_dots(tiff_src, channel, strictness, nbins, threshold)
        
        #print(f'{len(dot_analysis[1])=}')

        assert len(dot_analysis[1]) >0
        #---------------------------------------------------------------------
        
        
        #Gaussian Fit the dots
        #---------------------------------------------------------------------
        if bool_gaussian_fitting == True:
            dot_analysis = get_gaussian_fitted_dots(tiff_src, channel, dot_analysis[0])
        #---------------------------------------------------------------------
        
        
        #Center the dots
        #---------------------------------------------------------------------
        if bool_radial_center == True:
            dot_analysis = get_radial_centered_dots(tiff_src, channel, dot_analysis[0])
        #---------------------------------------------------------------------
        
        
        #Visualize Dots
        #---------------------------------------------------------------------
        median_z = tiff.shape[0]//2
        if bool_visualize_dots == True:# and z == median_z:
            get_visuals_3d(tiff_src, dot_analysis, tiff_3d[median_z], analysis_name, median_z)
        #---------------------------------------------------------------------
        
        #Shift Locations
        #---------------------------------------------------------------------
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
        #---------------------------------------------------------------------
        
        #Add channel dataframe to tiff dataframe
        #----------------------------------------------------------
        df_ch = add_hyb_and_ch_to_df(dot_analysis, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        #----------------------------------------------------------
        
    #Stack z dots
    #----------------------------------------------------------
    if bool_stack_z_dots:
        df_tiff.z = 1 
    #----------------------------------------------------------
    
    #Save to file
    #----------------------------------------------------------
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)
    #----------------------------------------------------------

     
    
if sys.argv[1] != 'debug_matlab_3d':
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
    parser.add_argument("--num_wav")
    parser.add_argument("--nbins")
    parser.add_argument("--threshold")
    parser.add_argument("--stack_z_s")
    parser.add_argument("--back_blob_removal")
    
    args, unknown = parser.parse_known_args()
    
    #print(f'{args.offset=}')
    
    print('hello')
    
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
                          args.back_subtract, channels, args.chromatic, str2bool(args.gaussian), \
                          str2bool(args.radial_center),int(args.strictness), args.z_slices, int(float(args.nbins)), \
                          int(args.threshold), args.num_wav, str2bool(args.stack_z_s), str2bool(args.back_blob_removal), args.rand)
        
else:
    print('Debugging')
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_1/MMStack_Pos0.ome.tif'
    offset = [0,0]
    channels = [1]
    analysis_name = 'takei_align'
    visualize_dots = True
    back_sub = False
    chromatic = False
    gaussian = False
    rad_center = False
    strictness = 5
    z_slices = None
    nbins= 100
    threshold= 300
    num_wav = 4
    rand_dir = '/home/nrezaee/temp'
    bool_stack_z_dots = True
    bool_blob_removal = True
    get_dots_for_tiff(tiff_src, offset, analysis_name, visualize_dots, back_sub, channels, \
                    chromatic, gaussian, rad_center, strictness, z_slices, nbins, \
                    threshold, num_wav, bool_stack_z_dots, bool_blob_removal, rand_dir)
                    
                    
                    
                    
                    
