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
sys.path.insert(0,'/home/nrezaee/test_cronjob_multi_dot')
from load_tiff import tiffy

def get_channel_offsets(tiff_dir, position, dst, num_wav):
    glob_me = os.path.join(tiff_dir, '*', position)
    tiff_dirs_dir = glob.glob(glob_me)
    #print(f'{tiff_dirs_dir=}')
    hyb_dirs = [hyb_dir for hyb_dir in tiff_dirs_dir if 'HybCycle_' in hyb_dir]
    print(f'{hyb_dirs=}')
    
    offsets = {}
    for hyb_dir in hyb_dirs:
        tiff_src = hyb_dir
        tiff = tiffy.load(tiff_src, num_wav=num_wav)
        shift, error, diffphase = phase_cross_correlation(tiff[0], tiff[1], upsample_factor = 100)
        print(f'{shift=}')
        offsets[tiff_src] = shift.tolist()
        
    
    import json 
    with open(dst, "w") as outfile: 
        json.dump(offsets, outfile)


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

def get_3_by_3(tiff_3d, df_locs, offset, hyb):
    
    #Add offset to points
    intensity_3_by_3 = []
    x_s = list(df_locs.x - offset[2])
    y_s = list(df_locs.y - offset[1])
    z_s = list(df_locs.z - offset[0]) 
    ints = list(df_locs.int)
    
    #Get 3x3 of of points in ch1
    for i in range(df_locs.shape[0]):
        
        if round(z_s[i])>=6:
            square_3 = tiff_3d[5:7,round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        elif round(z_s[i]) <= 1:
            square_3 = tiff_3d[0:2,round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        else:
            square_3 = tiff_3d[round(z_s[i]-1):round(z_s[i]+2),round(y_s[i]-1):round(y_s[i]+2), round(x_s[i]-1):round(x_s[i]+2)]
        
        # print(f'{x_s[i]=}')
        # print(f'{y_s[i]=}')
        # print(f'{square_3.shape=}')
        # print(f'{square_3=}')
        # print(f'{ints[i]=}')
        #(f'{i=}')
        #assert  np.any(square_3 == ints[i]) or square_3.shape[0] ==0 or square_3.shape[1]==0
        ave_square = np.sum(square_3)
        #print(f'{ave_square=}')
        intensity_3_by_3.append(ave_square)
        
    df_locs['sum_3x3_int_ch1'] = intensity_3_by_3
    print(f'{hyb=}')
    print('-------------------------------------------------')
    df_locs['hyb'] = np.full((df_locs.shape[0]), hyb)
    print(f'{df_locs.shape=}')
    return df_locs
    
    
def get_hyb_dirs(tiff_dir):
    glob_me = os.path.join(tiff_dir, '*')
    tiff_dirs_dir = glob.glob(glob_me)
    print(f'{tiff_dirs_dir=}')
    hyb_dirs = [hyb_dir for hyb_dir in tiff_dirs_dir if 'HybCycle_' in hyb_dir]
    print(f'{hyb_dirs=}')
    return hyb_dirs
    
def get_loaded_tiff(hyb_dirs, position, hyb, num_wav):
    hyb_dir_list = [hyb_dir for hyb_dir in hyb_dirs if str(hyb) in hyb_dir.split(os.sep)[-1]]
    assert len(hyb_dir_list) == 1
    hyb_dir = hyb_dir_list[0]
    tiff_src = os.path.join(hyb_dir, position)
    tiff = tiffy.load(tiff_src, num_wav=num_wav)
    return tiff, tiff_src
#Set Position
def get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst, num_wav):
    #Set Offset across Hybs
    with open(offsets_src) as json_file:
        offsets = json.load(json_file)
       
    #Set Locations csv
    df_locs = pd.read_csv(locations_src)

    #Get Hyb Dirs
    hyb_dirs = get_hyb_dirs(tiff_dir)
    
    #Get locations csv
    df_locs = pd.read_csv(locations_src)
    print(f'{df_locs=}')
    df_new_locs = pd.DataFrame(columns=['hyb', 'ch', 'x','y','z','int','sum_3x3_int_ch1'])
    
    #Get Each Hyb
    position = 'MMStack_Pos' + str(pos) + '.ome.tif'
    for hyb in df_locs.hyb.unique():
        
        #Get the Tiff src
        # hyb_dir_list = [hyb_dir for hyb_dir in hyb_dirs if str(hyb) in hyb_dir.split(os.sep)[-1]]
        # assert len(hyb_dir_list) == 1
        # hyb_dir = hyb_dir_list[0]
        # tiff_src = os.path.join(hyb_dir, position)
        # tiff = tiffy.load(tiff_src, num_wav=3)    
        tiff, tiff_src = get_loaded_tiff(hyb_dirs, position, hyb, num_wav=num_wav)
        
        #Load tiff and get right dots and offset
        tiff_ch = tiff[:,0,:,:]
        df_hyb_ch = df_locs[(df_locs.hyb == df_locs.hyb.min()) & (df_locs.ch == 1)]
        offset = offsets[(os.sep).join(tiff_src.split(os.sep)[-2:])]
        
        #Get the 3x3 of image
        df_new_locs = df_new_locs.append(get_3_by_3(tiff_ch, df_hyb_ch, offset, hyb))
        # print(f'{df_new_locs.columns=}')
        print(f'{df_new_locs.shape=}')
        
    df_new_locs.to_csv(dst, index=False)
    
if sys.argv[1] == 'debug_lampfish_ch1':
    pos = 0
    offsets_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/offsets.json'
    locations_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos_strict_8/MMStack_Pos1/Dot_Locations/locations.csv'
    tiff_dir = '/groups/CaiLab/personal/Linus/raw/5ratiometric_test'
    get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst='foo/lampfish_decoding_ch1.csv' + str(pos)+'.csv')
    
elif sys.argv[1] == 'debug_lampfish_ch1_test1':
    pos = 0
    offsets_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/offsets.json'
    locations_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/Dot_Locations/locations.csv'
    tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1'
    get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst='foo/lampfish_decoding__test_ch1.csv', num_wav=4)   
    


        
        

