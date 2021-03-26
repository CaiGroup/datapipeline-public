import os 
import numpy as np
import sys
sys.path.insert(0, os.getcwd())
from align_scripts.fiducial_marker_helpers.get_fiducial_dots_in_tiff import get_dots_for_tiff
from align_scripts.fiducial_marker_helpers.FMAligner import FMAligner
import pandas as pd

from scipy.io import loadmat
import pandas as pd

def get_converted_df(locs_src, dst):

    loc_var = loadmat(locs_src)
    points = loc_var['points']
    intensities = loc_var['intensity']
    print(f'{points.shape=}')
    print(f'{intensities.shape=}')
    
    for i in range(intensities.shape[0]):

        channel = (i%3) + 1
        hyb = i//3 + 1

        print(f'{points[i][0].shape=}')
        print(f'{intensities[i][0].shape=}')
        points_and_ints = np.concatenate((points[i][0], intensities[i][0]), axis =1)

        channel_row =  np.full((points_and_ints.shape[0], 1), channel)
        points_ints_hyb = np.concatenate((channel_row, points_and_ints), axis =1)

        hyb_row =  np.full((points_and_ints.shape[0], 1), channel)
        points_ints_hyb_ch = np.concatenate((hyb_row, points_ints_hyb), axis =1)

        print(f'{points_ints_hyb_ch.shape=}')

        if i == 0:
            all_points = points_ints_hyb_ch
        else:
            all_points = np.concatenate((all_points, points_ints_hyb_ch))

        print(f'{all_points.shape=}')

    df_points = pd.DataFrame({'ch':all_points[:,0], 'hyb':all_points[:,1], \
                              'x':all_points[:,2], 'y':all_points[:,3], \
                              'z':all_points[:,4], 'int':all_points[:,5]})
    df_points = df_points.astype({"ch": int, "hyb": int})
    df_points.to_csv(dst, index = False)
    
    return df_points

def get_df_locs_for_ref(locs, dst):
    
    all_channels = []
    for i in range(locs.shape[0]):
        
    
        channel = (i%3) + 1
        print(f'{channel=}')
        points_ints = []
        for j in range(len(locs[i][0])):
            locs[i][0][j].append(locs[i][1][j])
            points_ints.append(locs[i][0][j])

        points_ints = np.asmatrix(points_ints)
        points_ints[:,[0,2]] =points_ints[:,[2,0]]
        
        channel_row =  np.full((points_ints.shape[0], 1), channel)
        points_ints_ch = np.concatenate((channel_row, points_ints), axis =1)
        
        if i == 0:
            all_channels = points_ints_ch
        else:
            all_channels = np.concatenate((all_channels, points_ints_ch), axis = 0)
            
  


    df_points = pd.DataFrame(all_channels, columns =['ch', 'x', 'y', 'z', 'int'])
    df_points = df_points.astype({"ch": int})
    print(f'{dst=}')
    df_points.to_csv(dst, index = False)
    
    return df_points
        

def get_fiducial_offset(data_dir, position, dst_dir, locs_src, num_wav):
    
    fid_init_path = os.path.join(data_dir, 'initial_fiducials', position)
    fid_final_path = os.path.join(data_dir, 'final_fiducials', position)
    
    df_fid_final = get_dots_for_tiff(fid_final_path, num_wav, dst_dir)
    df_fid_init = get_dots_for_tiff(fid_init_path, num_wav, dst_dir)
    
    print(f'{df_fid_final}')
    print(f'{df_fid_init=}')
    
    df_points = pd.read_csv(locs_src)
    
    channels = list(range(1, int(num_wav) + 1 ))
    for channel in channels:
        ch_ref = df_fid_init.set_index("ch").loc[channel]
        ch_ro = df_points.set_index("ch").loc[channel].set_index("hyb")
        ch_ref_final = df_fid_final.set_index("ch").loc[channel]
    
        dal = FMAligner(ch_ro, ch_ref, ch_ref_final)
        dal.auto_set_params()
    
    
        dal.align()
        dal.save_offsets(os.path.join(dst_dir, "offsets_ch" + str(channel) + ".csv"))
        dal.save_matches(os.path.join(dst_dir,  "matches_ch" + str(channel) + ".csv"))
        dal.save_loocv_errors(os.path.join(dst_dir, "loov_errors_ch" + str(channel) + ".csv"))
        
    
import sys

if sys.argv[1] == 'debug_fiducials':
    sys.path.insert(0, os.getcwd())
    data_dir = '/groups/CaiLab/personal/nrezaee/raw/2020-10-19-takei/'
    pos_dir = '/groups/CaiLab/'
    position = 'MMStack_Pos0.ome.tif'
    locs_src = '/groups/CaiLab/analyses/nrezaee/2020-11-24-takei-2ch-1200/top_takei_1200mrna/MMStack_Pos0/Dot_Locations/locations.csv'
    dst_dir = 'foo'
    num_wav = 4
    get_fiducial_offset(data_dir, position, dst_dir, locs_src, num_wav)



