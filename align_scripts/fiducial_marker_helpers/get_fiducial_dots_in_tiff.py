import numpy as np
import tifffile as tf
import os
import warnings
import sys
import pandas as pd
import scipy 
import cv2
import matplotlib.pyplot as plt
sys.path.append(os.getcwd())

from load_tiff import tiffy
from dot_detection.helpers.visualize_dots import get_visuals_3d
from dot_detection.helpers.shift_locations import shift_locations
from dot_detection.helpers.background_subtraction import get_background
from align_scripts.fiducial_marker_helpers.fid_jump_helpers import hist_jump_threshed_3d
from dot_detection.gaussian_fitting_better.gaussian_fitting import get_gaussian_fitted_dots
from dot_detection.radial_center.radial_center_fitting import get_radial_centered_dots


def add_ch_to_df(dots_in_channel, tiff_src, channel):

    channel_array = np.full((len(dots_in_channel[1])), channel + 1)

    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['ch', 'x','y','z','int'])

    return df


def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel  = tuple(np.array(tiff_2d.shape)//num_tiles)
    blurry_img = cv2.blur(tiff_2d,blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return tiff_2d

def blur_back_subtract_3d(img_3d, num_tiles=1):
    
    for i in range(img_3d.shape[0]):
        img_3d[i,:,:] = blur_back_subtract(img_3d[i,:,:], num_tiles)
    return img_3d

def normalize(img, max_norm=1000):
    norm_image = cv2.normalize(img, None, alpha=0, beta=max_norm, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return norm_image

def tophat_2d(img_2d):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(20,20))*4
    tophat_img = cv2.morphologyEx(img_2d, cv2.MORPH_TOPHAT, kernel)
    return tophat_img

def tophat_3d(img_3d):
    print(f'{img_3d.shape=}')
    for i in range(len(img_3d)):
        print(f'{i=}')
        img_3d[i] = tophat_2d(img_3d[i])
    return img_3d

def preprocess_img(img_3d):
    #norm_img_3d = normalize(img_3d)
    blur_img_3d = blur_back_subtract_3d(img_3d)
    print(f'{blur_img_3d.shape=}')
    #blur_img_3d = tophat_3d(blur_img_3d)
    nonzero_img_3d = np.where(blur_img_3d < 0, 0, blur_img_3d)
    return nonzero_img_3d


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
    
    df = pd.DataFrame(data = dots_in_channel[0], columns=['x', 'y', 'z'])
    df['ch'] = channel_array
    df['int'] = dots_in_channel[1]
    df = df.reindex(columns=['ch', 'x','y','z','int'])

    return df

def get_dots_for_tiff(tiff_src,num_wav, dst, dot_radius, strictness=15):
    
    # #Getting Background Src
    # #--------------------------------------------------------------------
    # if bool_background_subtraction == True:
    #         background_src = get_background(tiff_src)
    #         print(f'{background_src=}')
    #         background = tiffy.load(background_src, num_wav)
    # #--------------------------------------------------------------------
    
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
    print("        Running on Channel:", end = " ", flush=True)
        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    # if channels_to_detect_dots=='all':
        
    channels = range(tiff.shape[1]-1)
    # else:
    #     channels = [int(channel)-1 for channel in channels_to_detect_dots]
    
    
    for channel in channels:
        
        dots_in_channel = None
        
        tiff_3d = tiff[:, channel,:,:]
        
        #tiff_3d = preprocess_img(tiff_3d)

        #Background Subtraction
        #---------------------------------------------------------------------
        # if bool_background_subtraction == True:
        #     # tiff_3d = run_back_sub(background, tiff_3d, channel, offset)
        #     assert background.shape == tiff.shape, "The background shape does not equal the tiff shape."
        #     print(f'{background.shape=}')
        #     print(f'{channel=}')
        #     tiff_3d = tiff_3d - background[:, channel]*1
        #     tiff_3d = np.where(tiff_3d < 0, 0, tiff_3d)
        #     tf.imwrite('foo.tif', tiff_3d)
        #---------------------------------------------------------------------

        print((channel+1), end = " ", flush =True)
        
        #Threshold on Biggest Jump
        #---------------------------------------------------------------------
        #strictness = 5
        print(f'{strictness=}')
        print(f'{tiff_3d.shape=}')
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, dot_radius))

        assert len(dot_analysis[1]) >0
        #---------------------------------------------------------------------
        
        
        #Gaussian Fit the dots
        #---------------------------------------------------------------------
        # if bool_gaussian_fitting == True:
        #     dot_analysis = get_gaussian_fitted_dots(tiff_src, channel, dot_analysis[0])
        # #---------------------------------------------------------------------
        
        # #Center the dots
        # #---------------------------------------------------------------------
        # if bool_radial_center == True:
        #     dot_analysis = get_radial_centered_dots(tiff_src, channel, dot_analysis[0])
        #---------------------------------------------------------------------
        
        dot_analysis[0][:, [0,2]] = dot_analysis[0][:, [2,0]]
    
        
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        df_ch = add_hyb_and_ch_to_df(dot_analysis, tiff_src, channel)
        df_tiff = df_tiff.append(df_ch)
        print(f'{df_tiff.shape=}')
        
        
    def get_fiducial_visual_debug(fid_tiff, fid_locs, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for channel in fid_locs.ch.unique():
            for i in range(fid_tiff[:, channel-1].shape[0]):
                locs_z = fid_locs[(fid_locs.z == i) & (fid_locs.ch == channel)]
                plt.figure(figsize=(40,40))
                plt.imshow(np.log(fid_tiff[i, channel]), cmap='gray')
                plt.scatter(locs_z.x, locs_z.y, facecolors='none', edgecolors='y', s=2000)
                png_dst = os.path.join(dst, 'channel_' +str(channel) + '_z_' + str(i) + '.png')
                #print(f'{png_dst=}')
                plt.savefig(png_dst)
                
    get_fiducial_visual_debug(tiff, df_tiff, dst)
    tf.imwrite('foo.tif', tiff)
    
    if not os.path.exists(dst):
        os.mkdir(dst)
    csv_path = os.path.join(dst,'locs.csv')
    print(f'{csv_path=}')
    df_tiff.to_csv(csv_path, index=False)
    
    return df_tiff
    
import sys
if sys.argv[1] == 'debug_fid_dot_detect':
    df_tiff = get_dots_for_tiff(tiff_src='/groups/CaiLab/personal/nrezaee/raw/2020-10-19-takei/initial_fiducials/MMStack_Pos0.ome.tif',
                                analysis_name='foo', \
                                bool_background_subtraction=False, 
                                channels_to_detect_dots=[1], 
                                bool_gaussian_fitting='False', \
                                strictness=15, 
                                bool_radial_center=False,
                                num_wav=4,
                                dot_radius=2,
                                dst='foo/final')
                                
    print(f'{type(df_tiff)=}')
    print(f'{df_tiff=}')

    
    
     