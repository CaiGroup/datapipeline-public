import numpy as np
import tifffile as tf
import os
import warnings
import sys
import pandas as pd
import scipy 
import cv2

sys.path.append(os.getcwd())
sys.path.append('../..')

from ...load_tiff import tiffy
from ..helpers.visualize_dots import get_visuals_3d
from ..helpers.shift_locations import shift_locations
from ..helpers.background_subtraction import get_background, get_back_sub_check, get_shifted_background, remove_blobs_with_masks_3d
from ..dot_detectors_3d.hist_jump_helpers.jump_helpers import hist_jump_threshed_3d
from ..gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots_python
from ..radial_center.radial_center_fitting import get_radial_centered_dots
from ..preprocessing.preprocess import preprocess_img, get_preprocess_check
from ..preprocessing.get_before_dot_detection_plots import side_by_side_preprocess_checks
from ..preprocessing.preprocess import get_preprocess_check, tophat_3d, blur_back_subtract_3d, blur_3d, dilate_3d


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

def get_dots_for_tiff(tiff_src, offset = [0,0,0], analysis_name = None, bool_visualize_dots = False, \
                      bool_background_subtraction = False, channels_to_detect_dots = [0], bool_chromatic = False, bool_gaussian_fitting = False, \
                      strictness = 5, bool_radial_center = False, z_slices = 'all', num_wav = 4, num_z = None, nbins= 100, dot_radius = 1, threshold = .0001, \
                      radius_step = 1, num_radii = 2, bool_stack_z_dots = False, bool_blob_removal = False, bool_rolling_ball = False, bool_tophat = False,
                      bool_tophat_raw_data = False, bool_blur = False, blur_kernel_size = 5, rolling_ball_kernel_size = 5, tophat_kernel_size = 100, 
                      tophat_raw_data_kernel_size = 0, overlap = .5, min_sigma = 1, max_sigma = 2, num_sigma = 2, bool_remove_bright_dots = True, 
                      dilate_background_kernel_size = 0, rand_dir= None):

    
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
        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    if channels_to_detect_dots=='all':
        channels = range(tiff.shape[1]-1)
    else:
        channels = [int(channel)-1 for channel in channels_to_detect_dots]
    
    
    for channel in channels:
        
        dots_in_channel = None
        
        tiff_3d = tiff[:, channel,:,:]
        
        if analysis_name != None:
            
            #Save Raw image to png file
            #---------------------------------------------------------------------
            get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Raw_Image')
            #---------------------------------------------------------------------

        
        #Run Tophat
        #---------------------------------------------------------------------
        print(f'{tophat_raw_data_kernel_size=}')
        if tophat_raw_data_kernel_size != 0:
            print('Running Tophat on Raw Data')
            tiff_3d = tophat_3d(tiff_3d, tophat_raw_data_kernel_size).astype(np.uint16)
            get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Tophat_Raw_Data_Check')
        #---------------------------------------------------------------------
        
        #Background Subtraction
        #---------------------------------------------------------------------
        if bool_background_subtraction == True:
            print(f'{background.shape=}')
            
            back_3d = get_shifted_background(background[:, channel], tiff_src, analysis_name)
            tiff_3d = cv2.subtract(tiff_3d, back_3d)
            
            if float(dilate_background_kernel_size) != 0:
                print('Dilating background by ', dilate_background_kernel_size)
                back_3d = dilate_3d(back_3d, dilate_background_kernel_size)
            
            
            tiff_3d = np.where(tiff_3d < 0, 0, tiff_3d)
            get_back_sub_check(tiff_src, analysis_name, tiff_3d, channel)
        #---------------------------------------------------------------------
        
        #Background Blob Removal
        #---------------------------------------------------------------------
        if bool_blob_removal == True:
            tiff_3d = remove_blobs_with_masks_3d(background[:, channel], tiff_3d, tiff_src, analysis_name, channel)
        #---------------------------------------------------------------------
        
        #Blur 3d
        #---------------------------------------------------------------------
        if bool_blur == True:
            tiff_3d = blur_3d(tiff_3d, blur_kernel_size)
            get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Blur_Check')
        #---------------------------------------------------------------------
        
        #Run Rolling Ball
        #---------------------------------------------------------------------
        if bool_rolling_ball == True:
            tiff_3d = blur_back_subtract_3d(tiff_3d, rolling_ball_kernel_size)
            get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Rolling_Ball_Check')
        #---------------------------------------------------------------------

        #Run Tophat
        #---------------------------------------------------------------------
        if bool_tophat == True:
            tiff_3d = tophat_3d(tiff_3d, tophat_kernel_size)
            get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Tophat_Check')
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
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, nbins, \
                        threshold, min_sigma, max_sigma, num_sigma, overlap, bool_remove_bright_dots))

        assert len(dot_analysis[1]) >0, 'No dots where found in image. Try decreasing threshold. (recommended .001)'
        #---------------------------------------------------------------------
        
        
        #Gaussian Fit the dots
        #---------------------------------------------------------------------
        if bool_gaussian_fitting == True:
            dot_analysis = get_gaussian_fitted_dots_python(tiff_src, channel, dot_analysis[0])
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
    
    #Remove Edges
    #----------------------------------------------------------
    df_tiff = df_tiff[(df_tiff.x < tiff.shape[2] - 5 ) 
                  & (df_tiff.y < tiff.shape[3] - 5)  
                  & (df_tiff.y > 5) 
                  & (df_tiff.x > 5)]
    #----------------------------------------------------------
    
    if rand_dir != None:
        #Save to csv file
        #----------------------------------------------------------
        csv_path = os.path.join(rand_dir, 'locs.csv')
        print(f'{csv_path=}')
        df_tiff.to_csv(csv_path, index=False)
        #----------------------------------------------------------
    
    #Get side by side checks
    #----------------------------------------------------------
    if analysis_name != None and 'ipykernel' not in sys.argv[0]:
        side_by_side_preprocess_checks(tiff_src, analysis_name)
    #----------------------------------------------------------
    
    return df_tiff, tiff, tiff_3d

if __name__ == '__main__':

    if 'ipykernel' not in sys.argv[0]:
        print(f'{sys.argv=}')
        if 'debug' not in sys.argv[1]:
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
            parser.add_argument("--threshold")
            parser.add_argument("--num_radii")
            parser.add_argument("--radius_step")
            parser.add_argument("--stack_z_s")
            parser.add_argument("--back_blob_removal")
            parser.add_argument("--rolling_ball")
            parser.add_argument("--tophat")
            parser.add_argument("--tophat_raw_data")
            parser.add_argument("--blur")
            parser.add_argument("--blur_kernel_size")
            parser.add_argument("--rolling_ball_kernel_size")
            parser.add_argument("--tophat_kernel_size")
            parser.add_argument("--tophat_raw_data_kernel_size")
            parser.add_argument("--min_sigma")
            parser.add_argument("--max_sigma")
            parser.add_argument("--num_sigma")
            parser.add_argument("--bool_remove_bright_dots")
            parser.add_argument("--dilate_background_kernel_size")

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
            get_dots_for_tiff(tiff_src = args.tiff_src,
                                offset = offset,
                                analysis_name = args.analysis_name,
                                bool_visualize_dots = str2bool(args.vis_dots),
                                bool_background_subtraction = str2bool(args.back_subtract),
                                channels_to_detect_dots = channels,
                                bool_chromatic = str2bool(args.chromatic),
                                bool_gaussian_fitting = str2bool(args.gaussian),
                                strictness = int(args.strictness),
                                bool_radial_center = str2bool(args.radial_center),
                                z_slices = args.z_slices,
                                num_wav = args.num_wav,
                                num_z = args.num_z,
                                nbins = float(args.nbins),
                                threshold = float(args.threshold),
                                radius_step = float(args.radius_step),
                                num_radii = int(float((args.num_radii))),
                                bool_stack_z_dots = str2bool(args.stack_z_s),
                                bool_blob_removal = str2bool(args.back_blob_removal),
                                bool_rolling_ball = str2bool(args.rolling_ball),
                                bool_tophat = str2bool(args.tophat),
                                bool_blur = str2bool(args.blur),
                                blur_kernel_size = float(args.blur_kernel_size),
                                rolling_ball_kernel_size = float(args.rolling_ball_kernel_size),
                                tophat_kernel_size = float(args.tophat_kernel_size),
                                tophat_raw_data_kernel_size = float(args.tophat_raw_data_kernel_size),
                                min_sigma = float(args.min_sigma),
                                max_sigma = float(args.max_sigma),
                                num_sigma = float(args.num_sigma),
                                bool_remove_bright_dots = str2bool(args.bool_remove_bright_dots),
                                dilate_background_kernel_size = float(args.dilate_background_kernel_size),
                                rand_dir = args.rand)
            #----------------------------------------------------------


        elif sys.argv[1] == 'debug_biggest_jump_3d':

            print('Debugging')

            get_dots_for_tiff(tiff_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_12/MMStack_Pos0.ome.tif',
                                offset = [0,0,0],
                                analysis_name = 'anthony_test_1',
                                bool_visualize_dots = False,
                                bool_background_subtraction = True,
                                channels_to_detect_dots = [1],
                                bool_chromatic = False,
                                bool_gaussian_fitting= False,
                                strictness = 5 ,
                                bool_radial_center = False,
                                z_slices = 'all',
                                num_wav = 4,
                                num_z = 'None',
                                nbins = 100,
                                dot_radius = 1,
                                threshold = .0001,
                                radius_step = 1 ,
                                num_radii = 2,
                                bool_stack_z_dots = True,
                                bool_blob_removal = False,
                                bool_rolling_ball = False,
                                bool_tophat = False,
                                bool_remove_bright_dots = False,
                                bool_tophat_raw_data = True,
                                tophat_raw_data_kernel_size = 100,
                                dilate_background_kernel_size = 10
                                )