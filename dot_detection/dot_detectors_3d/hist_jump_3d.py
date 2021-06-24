import numpy as np
import tifffile as tf
import os
import warnings
import sys
import pandas as pd
import scipy 
import cv2

sys.path.append(os.getcwd())

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import get_visuals_3d
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import get_background, get_back_sub_check, get_shifted_background, remove_blobs_with_masks_3d
from dot_detection.dot_detectors_3d.hist_jump_helpers.jump_helpers import hist_jump_threshed_3d
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots
from dot_detection.preprocessing.preprocess import preprocess_img, get_preprocess_check


warnings.filterwarnings("ignore")

def add_hyb_and_ch_to_df(dots_in_channel, tiff_src, channel):
    """
    Add channel dataframe of dots to tiff dataframe of dots
        add channel and hyb columns in process
    """
    
    #Get hybs and channel columns
    #----------------------------------------------------------
    channel_array = np.full((len(dots_in_channel[1])), channel + 1)
    hyb = int(tiff_src.split('HybCycle_')[1].split('/MMStack')[0])
    hyb_array = np.full((len(dots_in_channel[1])), hyb)
    #----------------------------------------------------------
    
    #Add Hyb and channel column
    #----------------------------------------------------------
    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['hyb'] = hyb_array
    df['int'] = dots_in_channel[1]
    #----------------------------------------------------------
    
    #Reorganize columns
    #----------------------------------------------------------
    df = df.reindex(columns=['hyb', 'ch', 'x','y','z','int'])
    #----------------------------------------------------------
    
    return df

def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic, bool_gaussian_fitting, \
                      strictness, bool_radial_center, z_slices, num_wav, rand_dir, num_z, nbins, dot_radius, threshold, \
                      radius_step, num_radii, bool_stack_z_dots, bool_blob_removal):
    
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
    tiff = tiffy.load(tiff_src, num_wav, num_z)
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
        
        #Run Preprocessing
        #---------------------------------------------------------------------
        tiff_3d = preprocess_img(tiff_3d)
        get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel)
        #---------------------------------------------------------------------
        
        

        #Check if 2d Dot Detection
        #---------------------------------------------------------------------
        if z_slices == 'all':
            pass
        
        else:
            tiff_3d= np.array([tiff_3d[z_slices,:,:]])
        #---------------------------------------------------------------------

        #Threshold on Biggest Jump
        #---------------------------------------------------------------------
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, nbins, dot_radius, \
                        threshold, dot_radius, num_radii))

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
        
        #Switch the x,y,z into right positions
        #-------------------------------------------------------
        dot_analysis[0][:, [0,2]] = dot_analysis[0][:, [2,0]]
        #-------------------------------------------------------
        
        
        #Visualize Dots
        #--------------------------------------------------------------------
        median_z = tiff_3d.shape[0]//2
        if bool_visualize_dots == True:# and z == median_z:
            get_visuals_3d(tiff_src, dot_analysis, tiff_3d[median_z], analysis_name, median_z)
        #---------------------------------------------------------------------
        
        
        #Shift Locations
        #---------------------------------------------------------------------
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
        #---------------------------------------------------------------------
        
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        df_ch = add_hyb_and_ch_to_df(dot_analysis, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        #---------------------------------------------------------------------
        
    #Stack z dots
    #----------------------------------------------------------
    if bool_stack_z_dots:
        df_tiff.z = 1 
    #----------------------------------------------------------
    
    #Save to csv file
    #----------------------------------------------------------
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)
    #----------------------------------------------------------


if sys.argv[1] != 'debug_hist_3d':    
    def str2bool(v):
      return v.lower() == "true"
    
    #Set Args
    #----------------------------------------------------------
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
    parser.add_argument("--num_z")
    parser.add_argument("--nbins")
    parser.add_argument("--dot_radius")
    parser.add_argument("--threshold")
    parser.add_argument("--num_radii")
    parser.add_argument("--radius_step")
    parser.add_argument("--stack_z_s")
    parser.add_argument("--back_blob_removal")
    args, unknown = parser.parse_known_args()
    
    print(f'{args=}')
    #----------------------------------------------------------
    
    #Get offset from args
    #----------------------------------------------------------
    if args.offset2 == 'None':
        offset = [float(args.offset0), float(args.offset1)]
    else:    
        offset = [float(args.offset0), float(args.offset1), float(args.offset2)]
    #----------------------------------------------------------
    
    #Get Channels from args
    #----------------------------------------------------------
    if args.channels[0] == 'all':
        channels = 'all'
    else:
        channels = [int(i.replace('[', '').replace(']','').replace(',','')) for i in args.channels]
    #----------------------------------------------------------
    
    #Get z_slices from args
    #----------------------------------------------------------
    if args.z_slices != 'all':
        args.z_slices = int(args.z_slices)
    #----------------------------------------------------------
    
    #Run dot detection on tiff
    #----------------------------------------------------------
    get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, str2bool(args.vis_dots), \
                          str2bool(args.back_subtract), channels, args.chromatic, str2bool(args.gaussian), int(args.strictness), \
                          str2bool(args.radial_center), args.z_slices, args.num_wav, args.rand, args.num_z, args.nbins, float(args.dot_radius), \
                          float(args.threshold), float(args.radius_step), int(float((args.num_radii))), str2bool(args.stack_z_s),
                          str2bool(args.back_blob_removal))
    #----------------------------------------------------------
    
else:
    
    print('Debugging')

    get_dots_for_tiff(tiff_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_12/MMStack_Pos12.ome.tif', 
                        offset = [0,0,0], 
                        analysis_name = 'anthony_test_1', 
                        bool_visualize_dots = False, 
                        bool_background_subtraction = False, 
                        channels_to_detect_dots = [1], 
                        bool_chromatic = False, 
                        bool_gaussian_fitting= False, 
                        strictness = 5 , 
                        bool_radial_center = False, 
                        z_slices = 'all', 
                        num_wav = 4, 
                        rand_dir = '/home/nrezaee/temp', 
                        num_z = 'None', 
                        nbins = 100, 
                        dot_radius = 1, 
                        threshold = .0001, 
                        radius_step = 1 , 
                        num_radii = 2,
                        bool_stack_z_dots = True,
                        bool_blob_removal = True)
    
    
    
    
    
    
    
    