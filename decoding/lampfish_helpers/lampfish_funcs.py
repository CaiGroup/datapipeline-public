import os
import glob
from load_tiff import tiffy
import numpy as np
import sys

def get_hyb_dirs(tiff_dir):
    
    #Get the list of dirs in tiff_dir
    #------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    tiff_dirs_dir = glob.glob(glob_me)
    #------------------------------------------------
    
    #Get Only Hyb dirs
    #------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in tiff_dirs_dir if 'HybCycle_' in hyb_dir]
    print(f'{hyb_dirs=}')
    #------------------------------------------------
    
    return hyb_dirs
    
def get_loaded_tiff(hyb_dirs, position, hyb, num_wav):
    
    #Only get Hyb with number
    #------------------------------------------------
    hyb_dir_list = [hyb_dir for hyb_dir in hyb_dirs if str(hyb) in hyb_dir.split(os.sep)[-1]]
    assert len(hyb_dir_list) == 1
    hyb_dir = hyb_dir_list[0]
    #------------------------------------------------
    
    #Load tiff 
    #------------------------------------------------
    tiff_src = os.path.join(hyb_dir, position)
    tiff = tiffy.load(tiff_src, num_wav=num_wav)
    #------------------------------------------------
    return tiff, tiff_src
    
def get_3_by_3(tiff_3d, df_locs, offset, hyb, new_col_name):
    
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
        
        ave_square = np.sum(square_3)
        intensity_3_by_3.append(ave_square)
        
    df_locs[new_col_name] = intensity_3_by_3
    print(f'{hyb=}')
    print('-------------------------------------------------')
    df_locs['hyb'] = np.full((df_locs.shape[0]), hyb)
    return df_locs
    
    
def get_pixels(tiff_3d, df_locs, offset, hyb, new_col_name):
    
    #Add offset to points
    #---------------------------------------------------------------
    intensity_3_by_3 = []
    x_s = list(df_locs.x - offset[2])
    y_s = list(df_locs.y - offset[1])
    z_s = list(df_locs.z - offset[0]) 
    ints = list(df_locs.int)
    #---------------------------------------------------------------
    
    #Get 3x3 of of points in ch1
    #---------------------------------------------------------------
    for i in range(df_locs.shape[0]):
        intensity = tiff_3d[np.round(z_s[i]).astype(np.int16), np.round(y_s[i]).astype(np.int16), np.round(x_s[i]).astype(np.int16)]

        intensity_3_by_3.append(intensity)
        
    df_locs[new_col_name] = intensity_3_by_3
    df_locs['hyb'] = np.full((df_locs.shape[0]), hyb)
    return df_locs

    