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

from .lampfish_helpers.lampfish_funcs import get_hyb_dirs, get_loaded_tiff
from ..load_tiff import tiffy

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def plot_img(img, x_s,y_s,hyb):
    plt.figure(figsize=(40,40))
    plt.imshow(img,cmap='gray')
    plt.scatter(np.array(x_s)-.5, np.array(y_s)-.5, s=.1, color='r')
    
    temp_dir = 'check_imgs_ch2_pos' +str(pos)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    plt.savefig(os.path.join(temp_dir, 'Hyb_' + str(hyb) +'.png'))

def get_3_by_3(tiff_3d, df_locs, offset, hyb):
    
    #Add offset to points
    #---------------------------------------------------------------
    intensity_3_by_3 = []
    x_s = list(df_locs.x - offset[2])
    y_s = list(df_locs.y - offset[1])
    z_s = list(df_locs.z - offset[0]) 
    ints = list(df_locs.int)
    #---------------------------------------------------------------

        
    for i in range(df_locs.shape[0]):
        z_max = tiff_3d.shape[0]
        #---------------------------------------------------------------
        if round(z_s[i])>=z_max-2:
            square_3 = tiff_3d[z_max-2:z_max-1,round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        elif round(z_s[i]) <= 1:
            square_3 = tiff_3d[0:2,round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        else:
            square_3 = tiff_3d[round(z_s[i]-1):round(z_s[i]+2),round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        #---------------------------------------------------------------
        
        # print(f'{x_s[i]=}')
        # print(f'{y_s[i]=}')
        # print(f'{square_3.shape=}')
        # print(f'{square_3=}')
        # print(f'{ints[i]=}')
        #(f'{i=}')
        #assert  np.any(square_3 == ints[i]) or square_3.shape[0] ==0 or square_3.shape[1]==0
        ave_square = np.sum(square_3)
        intensity_3_by_3.append(ave_square)
        
    df_locs['sum_3x3_int_ch2'] = intensity_3_by_3
    print(f'{hyb=}')
    print('-------------------------------------------------')
    df_locs['hyb'] = np.full((df_locs.shape[0]), hyb)
    return df_locs

def get_ratio_second_channel(offset_src, channel_offset_src, locations_src, tiff_dir, pos, dst, num_wav):
    
    #Get Offset across Hybs
    #---------------------------------------------------------------
    with open(offset_src) as json_file:
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
        tiff_ch = tiff[:,0,:,:]
        #---------------------------------------------------------------
        
        #Get right locations
        #---------------------------------------------------------------
        df_hyb_ch = df_locs[(df_locs.hyb ==  df_locs.hyb.min()) & (df_locs.ch == 1)]
        #---------------------------------------------------------------
        
        #Get right offsets
        #---------------------------------------------------------------
        hyb_offset = np.array(offsets[(os.sep).join(tiff_src.split(os.sep)[-2:])])
        hyb_offset = hyb_offset #+ np.array(offsets_ch[tiff_src])#[::-1]
        #---------------------------------------------------------------
        
        #Get the 3x3 of image
        #---------------------------------------------------------------
        df_new_locs = df_new_locs.append(get_3_by_3(tiff_ch, df_hyb_ch, hyb_offset, hyb))
        print(f'{df_new_locs.shape=}')
        #---------------------------------------------------------------
        
    # I know what you are thinking 
    #   "Why did this idiot save and reload the dataframe?"
    # Well, for some reason I get a zero division error without saving and loading it
    # I have no clue why but that is just how it is
    # so please dont make fun of me
    
    #Get Ratio and save dataframe
    #---------------------------------------------------------------
    df_new_locs.to_csv(dst, index=False)
    df_new_locs = pd.read_csv(dst)
    df_new_locs['ratio'] = df_new_locs['sum_3x3_int_ch1'].astype(np.float64)/(df_new_locs['sum_3x3_int_ch2'] + df_new_locs['sum_3x3_int_ch1'])
    df_new_locs.to_csv(dst, index=False)
    #---------------------------------------------------------------

if sys.argv[1] == 'debug_lampfish_ch2':
    pos=0
    offsets_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/offsets.json'
    channel_offsets_src = 'foo/channel_offsets.json'
    locations_src = 'foo/lampfish_decoding_ch1.csv' + str(pos)+'.csv'
    tiff_dir = '/groups/CaiLab/personal/Linus/raw/5ratiometric_test'
    get_ratio_second_channel(offset_src, channel_offset_src, locations_src, tiff_dir, pos)

elif sys.argv[1] == 'debug_lampfish_ch2_test1':
    pos = 0
    offsets_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/offsets.json'
    channel_offset_src = '/home/nrezaee/test_cronjob_multi_dot/foo/test_decoding_class/lampfish_test/channel_offsets.json'
    #locations_src = '/home/nrezaee/test_cronjob_multi_dot/foo/test_decoding_class/lampfish_test/lampfish_ratio_results_just_ch1.csv'
    locations_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/Dot_Locations/locations.csv'
    tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1'
    get_ratio_second_channel(offsets_src, channel_offset_src, locations_src, tiff_dir, pos, dst='foo/lampfish_decoding_test_ch2.csv', num_wav=4)   
        

