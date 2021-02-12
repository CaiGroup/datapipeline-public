
print(1)
import numpy as np
import os
import glob
import numpy as np
import warnings
import pandas as pd

import sys

sys.path.insert(0, os.getcwd())

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import plot_and_save_locations, get_visuals
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.helpers.shift_locations import shift_locations
print(1.25)
from dot_detection.helpers.background_subtraction import apply_background_subtraction
from dot_detection.helpers.background_subtraction import get_background
from dot_detection.helpers.add_z import add_z_col
print(1.3)

from dot_detection.helpers.threshold import apply_thresh
from dot_detection.helpers.compile_dots import add_to_dots_in_channel
print(1.4)
from dot_detection.helpers.hist_jump_helpers import get_hist_threshed_dots 
from dot_detection.helpers.remove_extra_dots import take_out_extra_dots
from dot_detection.dot_detectors_3d.matlab_dot_detection.matlab_dot_detector import get_matlab_detected_dots
print(1.5)
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots
print(2)
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
                      bool_radial_center, strictness, z_slices, nbins, threshold, rand_dir):
    
    #Getting Background Src
    #--------------------------------------------------------------------
   # back_src = get_background(tiff_src)
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
        
        
        #Remove Extra Dots Across Z slices
        #---------------------------------------------------------------------
        # if z_slices == 'all':
        #     dot_analysis = take_out_extra_dots(dot_analysis)
        #---------------------------------------------------------------------

        
        #Visualize Dots
        #---------------------------------------------------------------------
        median_z = tiff.shape[0]//2
        print(f'{bool_visualize_dots=}')
        if bool_visualize_dots == True:# and channel == 1 and z == median_z:
            get_visuals(tiff_src, dot_analysis, tiff_3d[median_z], analysis_name)
        #---------------------------------------------------------------------
        
        #Shift Locations
        #---------------------------------------------------------------------
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)
        #---------------------------------------------------------------------
        
        df_ch = add_hyb_and_ch_to_df(dot_analysis, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)


     
    

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
parser.add_argument("--nbins")
parser.add_argument("--threshold")


args, unknown = parser.parse_known_args()

#print(f'{args.offset=}')

print('hello')
print(f'{sys.argv[1]=}')
if sys.argv[1] != 'debug_main':
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
                          args.back_subtract, channels, args.chromatic, str2bool(args.gaussian), \
                          str2bool(args.radial_center),int(args.strictness), args.z_slices, int(args.nbins), \
                          int(args.threshold), args.rand)
    
else:
    print('Debugging')
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei-preprocessed/HybCycle_0/MMStack_Pos0.ome.tif'
    offset = [0,0,0]
    channels = 'all'
    analysis_name = None
    n_dots = 10
    rand_dir = '/home/nrezaee/temp'
    radial_center = True
    get_dots_for_tiff(tiff_src, offset, analysis_name, False, False, channels, False, False, radial_center, 8, None, 100, \
                    300, rand_dir)
