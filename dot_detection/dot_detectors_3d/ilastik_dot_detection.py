# from __future__ import annotations
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
import tifffile
import tempfile
import subprocess

from load_tiff import tiffy
from dot_detection.visualize_dots.tiff_visuals import plot_and_save_locations
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.dot_detectors_2d.dot_detector_2d import find_dots

warnings.filterwarnings("ignore")


def add_offset_to_locations(locations, offset):

    locations_offsetted = [location + offset for location in locations]
    
    return locations_offsetted

def remove_out_of_place_locs(dot_analysis, upper_bound = 2048, lower_bound = 0, debug =False):
    len_locs = len(dot_analysis[0])

    i=0
    out_of_place = []
    while i < len_locs:
        if (dot_analysis[0][i] < upper_bound).all() and (dot_analysis[0][i] > lower_bound).all():
            #print('Keeping', locations_offsetted[i])
            i+=1
            pass
        else: 
            print('OUt of boudns deletion')
            out_of_place.append(dot_analysis[0][i])
            
            dot_analysis[0] = np.delete(dot_analysis[0], i, axis=0)
            dot_analysis[1] = np.delete(dot_analysis[1], i)
            
            i-=1
            len_locs=len(locations_offsetted)
            #print(f'{i=}')
    
    if debug == True:
        
        return dot_analysis, out_of_place
    
    if debug == False:
        
        return dot_analysis


def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic):
    
    
    #Getting Background Src
    #--------------------------------------------------------------------
    if bool_background_subtraction == True:
        tiff_split = tiff_src.split(os.sep)
        tiff_split[-2] = 'background'
        background_src = (os.sep).join(tiff_split)
        
        background = tiffy.load(background_src)
        background = background[:,[0,2,1,3],:,:]
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
    
    
    #Print RUnning Chromatic Abberation
    #---------------------------------------------------------------------
    if bool_chromatic ==True:
        print("        Shifting image for Chromatic Abberation", flush=True)
    #---------------------------------------------------------------------
    
    
    
    print("        Running on Channel:", end = " ", flush=True)
        
    #Loops through channels for Dot Detection
    #---------------------------------------------------------------------
    if channels_to_detect_dots=='all':
        
        channels = range(tiff.shape[1]-1)
    else:
        channels = [int(channel)-1 for channel in channels_to_detect_dots]
    #---------------------------------------------------------------------
        
        
    #Declare tmp directory
    #---------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    temp_file_pngs = []
    print(f'{temp_dir.name=}')
    #---------------------------------------------------------------------
    
    
    for channel in channels:
        
        tiff_3d = tiff[:, channel,:,:]
        
        # print((channel+1), end = " ", flush =True)
        
        dots_in_channel = None
        
        
        #Loops through Z-stacks to create temporary tiff files
        #---------------------------------------------------------------------
        for z in range(tiff_shape[0]):
            
            tiff_2d = tiff_3d[z, :, :]
            
            if bool_background_subtraction == True:
                
                background3d = scipy.ndimage.interpolation.shift(background[:,channel,:,:], np.negative(offset))
            
                background_2d = background3d[0,:,:]
                
                tiff_2d = cv2.subtract(tiff_2d, background_2d)

            if bool_normalization == True:
                
                minimum = np.min(tiff_2d)
                maximum = np.max(tiff_2d)
                
                tiff_2d = cv2.normalize(tiff_2d,  None, minimum, maximum, cv2.NORM_MINMAX)
                
                
            #Create Temp file 
            #---------------------------------------------------------------------
            
            
            file_name = "Ch" + str(channel) + 'Z' + str(z) + '.png'
            
            temp_file_png = os.path.join(temp_dir.name, file_name)
            
            temp_file_pngs.append(temp_file_png)
            
            tiff_8bit = (cv2.normalize(tiff_2d, None, 0, 100, norm_type=cv2.NORM_MINMAX))
            
            tifffile.imwrite(temp_file_png, tiff_8bit)
            #---------------------------------------------------------------------
        #---------------------------------------------------------------------
    
    
    #Run ilastik probabilities
    #---------------------------------------------------------------------
    #print("Contents of tmpdir", os.listdir(temp_dir.name))
    
    temp_dir_for_probs =  tempfile.TemporaryDirectory()
    
    temp_file_for_probs = os.path.join(temp_dir_for_probs.name, '{nickname}.png')
    
    cmd = '/groups/CaiLab/personal/nrezaee/ilastik/ilastik-1.3.3post3-Linux/run_ilastik.sh --headless --project=/groups/CaiLab/personal/nrezaee/ilastik/projects/intron_trained_with_Hyb0_100pi-less-dots1.ilp --export_source="Probabilities" --output_format=png --output_filename_format={} '
    
    cmd = cmd.format(temp_file_for_probs)
    
    for temp_file_png in temp_file_pngs:
        cmd = cmd + ' ' + temp_file_png
        
    #print(f'{cmd=}')
    
    os.system(cmd)
    
    prob_files = os.listdir(temp_dir_for_probs.name)
            
    #print('Contents of returned tempdir', prob_files)      
    #---------------------------------------------------------------------
    
    
    
    #Run Dot detection on probabilities
    #---------------------------------------------------------------------
    for channel in channels:
        
        dots_in_channel = None
        
        #Get Probability files for channel
        #---------------------------------------------------------------------
        channel_probs = []
    
        for prob_file in prob_files:
            channel_number = int(prob_file.split('Ch')[1].split('Z')[0])
            if channel_number == channel:
                channel_probs.append(prob_file)
        #---------------------------------------------------------------------
        
        
        for channel_prob in channel_probs:
            print(f'{channel_prob=}')
            tiff_probs = imageio.imread(os.path.join(temp_dir_for_probs.name, channel_prob))
            
            tiff_2d = tiff_probs[:,:,0]
            
            
            z_stack = int(channel_prob.split('Z')[1].split('.png')[0])
            
            #Get dots from 2d image
            #---------------------------------------------------------------------
            dot_analysis = list(find_dots(tiff_2d))
            #---------------------------------------------------------------------
            
            
            #Add Z column to dot locations
            #---------------------------------------------------------------------
            number_of_dots = dot_analysis[0].shape[0]
            
            z_column = np.full((number_of_dots,1), z)
            
            dot_analysis[0] = np.append(dot_analysis[0], z_column, 1)
            #---------------------------------------------------------------------
            
            
            #Switch [y, x, z] to [x, y, z]
            #---------------------------------------------------------------------
            dot_analysis[0][:,[0,1]] = dot_analysis[0][:,[1,0]]
            #---------------------------------------------------------------------
            
            
            #Shift for alignment
            #--------------------------------------------------------------------
            if np.all(offset == [0, 0, 0]):
                
                #No Shifting :( 
                
                pass
            
            else:
                
                offset = np.array(offset)
                
                if bool_chromatic==True:
                    
                    split_tiff_src = tiff_src.split(os.sep)
                
                    personal = split_tiff_src[4]
                    
                    experiment_name= split_tiff_src[6]
                    
                    chromatic_offsets_src = os.path.join('/groups/CaiLab/analyses', personal, experiment_name, \
                                            analysis_name, 'Chromatic_Abberation_Correction/chromatic_offsets.json')
                                            
                    with open(chromatic_offsets_src) as json_file: 
                        chromatic_offsets = np.array(json.load(json_file))
                        
                    #---------------------------------------------------------------------
                    
                    
                    #Shift for chromatic abberation
                    #---------------------------------------------------------------------
                    key  = "Channel " +str(channel)
                    
                    if chromatic_offsets[key] != [0,0,0]:
                        
                        offset = offset + chromatic_offset
                    #---------------------------------------------------------------------
 
                print("        Shifting locations for Alignment", flush=True)
                
                
                #Shifting Dot locations
                print('Shifting Dot Locations')
                dot_analysis[0] = add_offset_to_locations(dot_analysis[0], np.array(offset))
                
                #Removing OUt of place dots
                #dot_analysis = np.array(remove_out_of_place_locs(dot_analysis))
            #---------------------------------------------------------------------            


            #Threshold Dots
            #---------------------------------------------------------------------
            amount_of_dots_you_want_in_each_image = 13000
            number_of_dots = len(dot_analysis[1])
            
            if number_of_dots < amount_of_dots_you_want_in_each_image:
                
                pass
            
            else:
                print("Deleting some dots")
                percentile = 100 - (amount_of_dots_you_want_in_each_image/number_of_dots)*100
                
                threshold = np.percentile(dot_analysis[1], percentile)

                index = 0
                dots_deleted = []
                #len_of_dot_analysis = len(dot_analysis[1])
                while (index < len(dot_analysis[1])):
                    if dot_analysis[1][index] <= threshold:
                        #print('Deleting', dot_analysis[1][index])

                        dot_analysis[0] = np.delete(dot_analysis[0], index, axis =0)
                        dot_analysis[1] = np.delete(dot_analysis[1], index)
                        
                        #len_of_dot_analysis = len(dot_analysis[1])
                        
                        #assert len_of_dot_analysis == len(dot_analysis[1])
                    
                        index-=1
                        
                        dots_deleted.append(index)
                    index+=1
                
                print(f'{len(dots_deleted)=}')
                    
            
                print(f'{len(dot_analysis[1])=}', flush =True)
                    
            #---------------------------------------------------------------------

            
            
            #Define Dots in Channel
            #---------------------------------------------------------------------
            if dots_in_channel == None:
                if np.array(dot_analysis[0]).shape != (0,3):

                    dots_in_channel = dot_analysis
            #---------------------------------------------------------------------
            
            
            #Concatenate dots
            #---------------------------------------------------------------------
            else:
                
                if np.array(dot_analysis[0]).shape != (0,3):
                
                    dots_in_channel[0] = np.concatenate((dots_in_channel[0], dot_analysis[0])).tolist()
                    dots_in_channel[1] = np.concatenate((dots_in_channel[1], dot_analysis[1])).tolist()
                    print(f'{len(dots_in_channel[0])=}')

            #---------------------------------------------------------------------
            
        
        #Add dots to main dots in tiff
        #---------------------------------------------------------------------
        dots_in_tiff.append(dots_in_channel)
        print(f'{len(dots_in_tiff)=}')
        #---------------------------------------------------------------------
        
     #-----------------------------------------------------------------
     
    print("")

    return dots_in_tiff
            
