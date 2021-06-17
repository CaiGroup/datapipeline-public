import os
import glob
import json
import random
import numpy as np
import tifffile as tf
import sys
sys.path.insert(0, '/home/nrezaee/data-pipeline')
from load_tiff import tiffy
from scipy.ndimage import shift
    
def get_stacked_dapi_s_align_check(offset_path, dst, num_wav=4, num_dapi_stacked= 10):
    """
    Creates a stacked Dapi img to check alignment
    """
    #Get all Hyb Dirs
    #--------------------------------------------------------
    split_data_dir = (offset_path).split(os.sep)
    personal = split_data_dir[4]
    exp_name = split_data_dir[5]
    position_ome_tiff = split_data_dir[7] + '.ome.tif'
    
    glob_hyb_dirs = os.path.join('/groups/CaiLab/personal', personal, 'raw', exp_name, 'HybCycle_*', position_ome_tiff)
    #print(f'{glob_hyb_dirs=}')
    
    all_hyb_dirs = glob.glob(glob_hyb_dirs)
    #print(f'{all_hyb_dirs=}')
    #--------------------------------------------------------
    
    
    #Read in offsets
    #--------------------------------------------------------
    with open(offset_path) as json_file:
        data_dict = json.load(json_file)
        #print(f'{data_dict=}')
    #--------------------------------------------------------
    
    
    #Loop through random hyb_dirs to get offset
    #--------------------------------------------------------
    stacked_dapi_s = []
    for hyb_dir in all_hyb_dirs:
        
        #Read in offset
        #--------------------------------------------------------
        key = "/".join(hyb_dir.split(os.sep)[-2:])
        offset = data_dict[key]
        print(f'{data_dict[key]=}')
        #--------------------------------------------------------
        
        #Read in image
        #--------------------------------------------------------
        tiff = tiffy.load(hyb_dir, num_wav)
        dapi_channel = -1
        dapi_3d = tiff[:, dapi_channel]
        
        #Shift Image
        #--------------------------------------------------------
        if len(offset) == 2:
            dapi_2d = dapi_3d[len(dapi_3d)//2]
            shifted_dapi_2d = shift(dapi_2d, offset)
        elif len(offset) == 3:
            shifted_dapi_3d = shift(dapi_3d, offset)
            shifted_dapi_2d = shifted_dapi_3d
            
        x_min = round((shifted_dapi_2d.shape[0]/5)*2)
        x_max = round((shifted_dapi_2d.shape[1]/5)*3)
        y_min = round((shifted_dapi_2d.shape[0]/5)*2)
        y_max = round((shifted_dapi_2d.shape[1]/5)*3)
                
        print(f'{shifted_dapi_2d.shape=}')
        stacked_dapi_s.append(shifted_dapi_2d[x_min:x_max, y_min:y_max])
        #--------------------------------------------------------
    
    stacked_dapi_s = np.array(stacked_dapi_s)
    print(f'{stacked_dapi_s.shape=}')
    
    tf.imwrite(dst, stacked_dapi_s,imagej=True)
    print(f'{dst=}')
    #--------------------------------------------------------
    
if sys.argv[1] == 'debug_align_visual_check':
    offset_path = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_debug_2_strict_8/MMStack_Pos0/offsets.json'
    dst = 'foo.tif'
    get_stacked_dapi_s_align_check(offset_path, dst)

elif sys.argv[1] == 'debug_align_visual_check_small':
    offset_path = '/groups/CaiLab/analyses/nrezaee/test1/align_test2/MMStack_Pos0/offsets.json'
    dst = 'foo.tif'
    get_stacked_dapi_s_align_check(offset_path, dst)

