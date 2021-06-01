import numpy as np
import tifffile as tf
import os
import warnings
import sys
import pandas as pd
import scipy 

sys.path.append(os.getcwd())

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import get_visuals_3d
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import get_background, get_back_sub_check
from dot_detection.dot_detectors_3d.hist_jump_helpers.jump_helpers import hist_jump_threshed_3d
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots


def run_back_sub(background, tiff_3d, channel, offset):
    
    print(f'{type(offset)=}')
    print(f'{type(offset)=}')
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
                      strictness, bool_radial_center, z_slices, num_wav, rand_dir, num_z, nbins, dot_radius, threshold, \
                      radius_step, num_radii):
    
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
            tiff_3d = tiff_3d.astype(np.int32) - background[:, channel].astype(np.int32)*.001
            tiff_3d = np.where(tiff_3d < 0, 0, tiff_3d)
            get_back_sub_check(tiff_src, analysis_name, tiff_3d)
        #---------------------------------------------------------------------

        print((channel+1), end = " ", flush =True)
        
        #Check if 2d Dot Detection
        #---------------------------------------------------------------------
        if z_slices == 'all':
            pass
        
        else:
            tiff_3d= np.array([tiff_3d[z_slices,:,:]])
        #---------------------------------------------------------------------

        #Threshold on Biggest Jump
        #---------------------------------------------------------------------
        #strictness = 5
        print(f'{strictness=}')
        print(f'{tiff_3d.shape=}')
        print(f'{threshold=}')
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, nbins, dot_radius, \
                        threshold, dot_radius, num_radii))

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
        
        dot_analysis[0][:, [0,2]] = dot_analysis[0][:, [2,0]]
        
        print(f'{dot_analysis[0]=}')
        
        #Visualize Dots
        #--------------------------------------------------------------------
        median_z = tiff_3d.shape[0]//2
        print(f'{bool_visualize_dots=}')
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
        
    tf.imwrite('foo.tif', tiff)
    
    csv_path = rand_dir +'/locs.csv'
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)


if sys.argv[1] != 'debug_hist_3d':    
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
    parser.add_argument("--num_z")
    parser.add_argument("--nbins")
    parser.add_argument("--dot_radius")
    parser.add_argument("--threshold")
    parser.add_argument("--num_radii")
    parser.add_argument("--radius_step")
    
    
    args, unknown = parser.parse_known_args()
    
    #print(f'{args.offset=}')
    
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

    
    get_dots_for_tiff(args.tiff_src, offset, args.analysis_name, str2bool(args.vis_dots), \
                          str2bool(args.back_subtract), channels, args.chromatic, str2bool(args.gaussian), int(args.strictness), \
                          str2bool(args.radial_center), args.z_slices, args.num_wav, args.rand, args.num_z, args.nbins, float(args.dot_radius), \
                          float(args.threshold), float(args.radius_step), int(float((args.num_radii))))

else:
    
    print('Debugging')
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_1/MMStack_Pos0.ome.tif'
    offset = [0,0,0]
    channels = 'all'
    analysis_name = 'linus_decoding'
    rand_dir = '/home/nrezaee/temp'
    vis_dots = True
    back_sub = True
    chromatic = False
    gauss = False
    rad = False
    strictness = 5
    z_slices = 'all'
    num_wav = 4
    num_z = 'None'
    nbins = 100
    dot_radius = 1
    threshold = .001
    num_radii = 2
    radius_step = 1
    get_dots_for_tiff(tiff_src, offset, analysis_name, vis_dots, back_sub, channels, chromatic, gauss, \
        strictness, rad, z_slices, num_wav, rand_dir, num_z, nbins, dot_radius, threshold, radius_step, num_radii)
    
    
    
    
    
    
    
    