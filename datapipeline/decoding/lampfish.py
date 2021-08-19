import os 
import pandas as pd
import glob
import tifffile as tf
import string
import random
import matplotlib.pyplot as plt
import numpy as np
import shutil
import sys
import json
import sys
from skimage.registration import phase_cross_correlation

from .lampfish_helpers.lampfish_funcs import get_hyb_dirs, get_loaded_tiff, get_3_by_3, get_pixels
from ..load_tiff import tiffy

def get_channel_offsets(tiff_dir, position, dst, num_wav):
    """
    Get offset channel by channel 
    """

    #Get path for each hyb dir
    #---------------------------------------------------------------
    hyb_dirs = get_hyb_dirs(tiff_dir)
    print(f'{hyb_dirs=}')
    #---------------------------------------------------------------
    
    
    #Get Offset for each hyb dir
    #---------------------------------------------------------------
    offsets = {}
    for hyb_dir in hyb_dirs:
        tiff_src = os.path.join(hyb_dir, position)
        tiff = tiffy.load(tiff_src, num_wav=num_wav, num_z=1)
        print(f'{tiff.shape=}')
        shift, error, diffphase = phase_cross_correlation(tiff[:,0], tiff[:,1], upsample_factor = 100)
        print(f'{shift=}')
        offsets[tiff_src] = shift.tolist()
    #---------------------------------------------------------------
        
    #Save Offsets
    #---------------------------------------------------------------
    with open(dst, "w") as outfile: 
        json.dump(offsets, outfile)
    #---------------------------------------------------------------

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def plot_img(img, x_s,y_s,hyb):
    plt.figure(figsize=(40,40))
    plt.imshow(img,cmap='gray')
    plt.scatter(np.array(x_s)-.5, np.array(y_s)-.5, s=.1, color='r')
    
    temp_dir = 'check_imgs_pos' +str(pos)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    plt.savefig(os.path.join(temp_dir, 'Hyb_' + str(hyb) +'.png'))


#Set Position
def get_ratio_of_channels(offsets_src, channel_offset_src, locations_src, tiff_dir, pos, dst, num_wav, lampfish_pixel):
    
    #Get Offset across Hybs
    #---------------------------------------------------------------
    with open(offsets_src) as json_file:
        offsets = json.load(json_file)
    #---------------------------------------------------------------
    
    #Get Offset across channels
    #---------------------------------------------------------------
    with open(channel_offset_src) as json_file:
        offsets_ch = json.load(json_file)
    #---------------------------------------------------------------
    
    #Get locations csv
    #---------------------------------------------------------------
    df_locs = pd.read_csv(locations_src)
    print(f'{df_locs=}')
    df_new_locs = pd.DataFrame(columns=['hyb', 'ch', 'x','y','z','int','sum_3x3_int_ch1', 'sum_3x3_int_ch2'])
    #---------------------------------------------------------------
    
    #Go through Each Hyb
    #---------------------------------------------------------------
    position = 'MMStack_Pos' + str(pos) + '.ome.tif'
    hyb_dirs = get_hyb_dirs(tiff_dir)
    for hyb in df_locs.hyb.unique():
        
        #Load the tiff 
        #---------------------------------------------------------------
        tiff, tiff_src = get_loaded_tiff(hyb_dirs, position, hyb, num_wav=num_wav)
        tiff_ch1 = tiff[:,0,:,:]
        tiff_ch2 = tiff[:,1,:,:]
        #---------------------------------------------------------------
        
        #Get right locations and offset
        #---------------------------------------------------------------
        df_hyb_ch = df_locs[(df_locs.hyb == df_locs.hyb.min()) & (df_locs.ch == 1)]
        offset_key = (os.sep).join(tiff_src.split(os.sep)[-2:])
        offset = np.insert(np.array(offsets[offset_key]), 0, 0)
        offset_ch = offset + np.array(offsets_ch[tiff_src])
        print(f'{df_hyb_ch.shape=}')
        #---------------------------------------------------------------
        
        #Remove Locations Outside tiff
        #---------------------------------------------------------------
        # df_hyb_ch = df_hyb_ch[(df_hyb_ch.z < tiff_ch1.shape[0]) & (df_hyb_ch.z > 0) & \
        #                         (df_hyb_ch.x < tiff_ch1.shape[1]) & (df_hyb_ch.x > 0) & \
        #                         (df_hyb_ch.y < tiff_ch1.shape[2]) & (df_hyb_ch.y > 0)]
        print(f'{df_hyb_ch.shape=}')
        #---------------------------------------------------------------
        
        
        #Get the 3x3 column 
        #---------------------------------------------------------------
        if lampfish_pixel == True:
            df_ch1 = get_pixels(tiff_ch1, df_hyb_ch, offset, hyb, new_col_name='sum_3x3_int_ch1' )
            df_ch1_ch2 = get_pixels(tiff_ch2, df_ch1, offset_ch, hyb, new_col_name='sum_3x3_int_ch2' )
        
        else:
            df_ch1 = get_3_by_3(tiff_ch1, df_hyb_ch, offset, hyb, new_col_name='sum_3x3_int_ch1' )
            df_ch1_ch2 = get_3_by_3(tiff_ch2, df_ch1, offset_ch, hyb, new_col_name='sum_3x3_int_ch2' )
 
        df_new_locs = df_new_locs.append(df_ch1_ch2)
        print(f'{df_new_locs.shape=}')
        #---------------------------------------------------------------
        
    #Save dataframe to csv
    #---------------------------------------------------------------
    df_new_locs.to_csv(dst, index=False)
    df_new_locs = pd.read_csv(dst)
    df_new_locs['ratio'] = df_new_locs['sum_3x3_int_ch1'].astype(np.float64)/(df_new_locs['sum_3x3_int_ch2'] + df_new_locs['sum_3x3_int_ch1'])
    df_new_locs.to_csv(dst, index=False)
    #---------------------------------------------------------------
if __name__ == '__main__':

    if sys.argv[1] == 'debug_lampfish_ch1':
        pos = 0
        offsets_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/offsets.json'
        locations_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos_strict_8/MMStack_Pos1/Dot_Locations/locations.csv'
        tiff_dir = '/groups/CaiLab/personal/Linus/raw/5ratiometric_test'
        get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst='foo/lampfish_decoding_ch1.csv' + str(pos)+'.csv')

    elif sys.argv[1] == 'debug_lampfish_ch1_test1':
        pos = 0
        offsets_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/offsets.json'
        channel_offset_src = '/home/nrezaee/test_cronjob_multi_dot/foo/test_decoding_class/lampfish_test/channel_offsets.json'
        locations_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/Dot_Locations/locations.csv'
        tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1'
        lampfish_pixel = True
        get_ratio_of_channels(offsets_src, channel_offset_src, locations_src, tiff_dir, \
                                pos, 'foo/lampfish_decoding.csv', 4, \
                                lampfish_pixel)

    elif sys.argv[1] == 'debug_lampfish_align':
        get_channel_offsets(tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/5ratiometric_test_max_int',
                            position = 'MMStack_Pos0.ome.tif',
                            dst = 'foo/channel_offsets_test.csv',
                            num_wav = 3)

    elif sys.argv[1] == 'debug_lampfish_max_int':
        pos = 0
        offsets_src = '/groups/CaiLab/analyses/nrezaee/5ratiometric_test_max_int/5ratio_all_pos_max_int_pos0/MMStack_Pos0/offsets.json'
        channel_offset_src = '/groups/CaiLab/analyses/nrezaee/5ratiometric_test_max_int/5ratio_all_pos_max_int_pos0/MMStack_Pos0/Decoded/channel_offsets.json'
        locations_src = '/groups/CaiLab/analyses/nrezaee/5ratiometric_test_max_int/5ratio_all_pos_max_int_pos0/MMStack_Pos0/Dot_Locations/locations.csv'
        tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/5ratiometric_test_max_int/'
        lampfish_pixel = True
        get_ratio_of_channels(offsets_src,
                            channel_offset_src,
                            locations_src,
                            tiff_dir,
                            pos,
                            'foo/lampfish_decoding.csv',
                            3, \
                            lampfish_pixel)
