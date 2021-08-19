import numpy as np
import os
import glob
import numpy as np
import warnings
import pandas as pd
import cv2
from scipy.io import savemat
import tifffile as tf
import sys

sys.path.insert(0, os.getcwd())

from ...load_tiff import tiffy
from ..helpers.visualize_dots import get_visuals_3d
from ..reorder_hybs import get_and_sort_hybs
from ..helpers.shift_locations import shift_locations
from ..helpers.background_subtraction import apply_background_subtraction
from ..helpers.background_subtraction import get_background, get_back_sub_check, get_shifted_background, remove_blobs_with_masks_3d
from ..helpers.add_z import add_z_col

from ..helpers.threshold import apply_thresh
from ..helpers.compile_dots import add_to_dots_in_channel
from ..helpers.hist_jump_helpers import get_hist_threshed_dots
from ..helpers.remove_extra_dots import take_out_extra_dots
from ..dot_detectors_3d.matlab_dot_detection.matlab_dot_detector import get_matlab_detected_dots
from ..gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from ..radial_center.radial_center_fitting import get_radial_centered_dots
from ..preprocessing.get_before_dot_detection_plots import side_by_side_preprocess_checks
from ..preprocessing.preprocess import preprocess_img, get_preprocess_check, tophat_3d, blur_back_subtract_3d, blur_3d

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
    

def get_dots_for_tiff(tiff_src, offset = [0,0,0] , analysis_name = None, bool_visualize_dots = False, \
                      bool_background_subtraction = False, channels_to_detect_dots = [0], bool_chromatic = False, bool_gaussian_fitting = False, \
                      bool_radial_center = False, strictness = 5, z_slices = None, nbins = 100, threshold = 300, num_wav = 4, bool_stack_z_dots = False, 
                      bool_blob_removal = False, bool_rolling_ball = False, bool_tophat = False, bool_blur = False, blur_kernel_size = 5, rolling_ball_kernel_size =5, 
                      tophat_kernel_size =5, rand_dir = '/tmp'):
    
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
        
        #Save Raw image to png file
        #---------------------------------------------------------------------
        get_preprocess_check(tiff_src, analysis_name, tiff_3d, channel, 'Raw_Image')
        #---------------------------------------------------------------------
        
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
        
        #Save tiff 3d mat
        #---------------------------------------------------------------------
        tiff_3d_mat_dst = os.path.join(rand_dir, 'tiff_3d.mat')
        
        savemat(tiff_3d_mat_dst, {'tiff_ch': tiff_3d})
        #---------------------------------------------------------------------

        
        #Threshold on Biggest Jump for matlab 3d
        #---------------------------------------------------------------------
        dot_analysis = get_matlab_detected_dots(tiff_3d_mat_dst, channel, strictness, nbins, threshold)
        
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

    #Get side by side checks
    #----------------------------------------------------------
    side_by_side_preprocess_checks(tiff_src, analysis_name)
    #----------------------------------------------------------
    
    return df_tiff, tiff

if __name__ == '__main__':

    if 'ipykernel' not in sys.argv[0]:
        print(f'{sys.argv=}')
        if 'debug' not in sys.argv[1]:
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
            parser.add_argument("--rolling_ball")
            parser.add_argument("--tophat")
            parser.add_argument("--blur")
            parser.add_argument("--blur_kernel_size")
            parser.add_argument("--rolling_ball_kernel_size")
            parser.add_argument("--tophat_kernel_size")

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


            get_dots_for_tiff(tiff_src = args.tiff_src,
                                offset =offset,
                                analysis_name = args.analysis_name,
                                bool_visualize_dots = str2bool(args.vis_dots),
                                bool_background_subtraction = args.back_subtract,
                                channels_to_detect_dots = channels,
                                bool_chromatic = args.chromatic,
                                bool_gaussian_fitting = str2bool(args.gaussian),
                                bool_radial_center = str2bool(args.radial_center),
                                strictness = int(args.strictness),
                                z_slices = args.z_slices,
                                nbins = int(float(args.nbins)),
                                threshold = int(float(args.threshold)),
                                num_wav = args.num_wav,
                                bool_stack_z_dots = str2bool(args.stack_z_s),
                                bool_blob_removal = str2bool(args.back_blob_removal),
                                bool_rolling_ball = str2bool(args.rolling_ball),
                                bool_tophat = str2bool(args.tophat),
                                bool_blur = str2bool(args.blur),
                                blur_kernel_size = float(args.blur_kernel_size),
                                rolling_ball_kernel_size = float(args.rolling_ball_kernel_size),
                                tophat_kernel_size = float(args.tophat_kernel_size),
                                rand_dir = args.rand)

        elif sys.argv[1] == 'debug_matlab_3d':

            print('Debugging')
            get_dots_for_tiff(tiff_src = '/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_4_corrected/HybCycle_4/MMStack_Pos3.ome.tif',
                            offset = [0,0],
                            analysis_name = 'jina_pseudos_4_corrected_pos3_strict_0_tophat_back_sub',
                            channels_to_detect_dots = [1],
                            strictness = 5,
                            num_wav = 4)

        elif sys.argv[1] == 'debug_matlab_3d_takei':

            print('Debugging')
            tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_4/MMStack_Pos0.ome.tif'
            offset = [0,0]
            channels = [1]
            analysis_name = 'takei_align'
            visualize_dots = False
            back_sub = False
            chromatic = False
            gaussian = False
            rad_center = False
            strictness = 0
            z_slices = None
            nbins= 100
            threshold= 300
            num_wav = 4
            rand_dir = 'foo/matlab_3d'
            os.makedirs(rand_dir, exist_ok= True)
            bool_stack_z_dots = False
            bool_blob_removal = False
            tophat = False
            rolling_ball = False
            get_dots_for_tiff(tiff_src, offset, analysis_name, visualize_dots, back_sub, channels,
                            chromatic, gaussian, rad_center, strictness, z_slices, nbins,
                            threshold, num_wav, bool_stack_z_dots, bool_blob_removal, rolling_ball, tophat,
                            rand_dir)
