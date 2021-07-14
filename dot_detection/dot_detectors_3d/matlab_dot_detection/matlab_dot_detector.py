import tempfile
import os
from scipy.io import loadmat
import numpy as np
import sys

def get_dot_analysis(mat_src):
    
    #Load points in from mat file
    #-------------------------------------------------------------------
    mat_info = loadmat(mat_src)
    points = mat_info['dots']
    print(f'{points.shape=}')
    #-------------------------------------------------------------------
    
    #Get histogram file
    #-------------------------------------------------------------------
    hist_src = os.path.join(os.path.dirname(mat_src), 'hist.png')
    #-------------------------------------------------------------------
    
    #Switch around the right way
    #-------------------------------------------------------------------
    # points[:, [2, 0]] = points[:, [0, 2]]
    # points[:, [2, 1]] = points[:, [1, 2]]
    # points[:, [0, 1]] = points[:, [1, 0]]
    #-------------------------------------------------------------------
    
    #Add in intensities
    #-------------------------------------------------------------------
    intensities = mat_info['thresh_ints']
    dot_analysis = [points, np.squeeze(intensities)]
    #-------------------------------------------------------------------
    
    return dot_analysis
    
def get_dot_locations_dir(tiff_src, analysis_name, channel):
    
    #Split Tiff src
    #------------------------------------------------
    all_analyses_dir = '/groups/CaiLab/analyses'
    
    splitted_tiff_src = tiff_src.split(os.sep)
    personal = splitted_tiff_src[4]
    exp_name = splitted_tiff_src[6]
    hyb = splitted_tiff_src[-2]
    pos = tiff_src.split(os.sep)[-1].split('.ome')[0]
    #------------------------------------------------
    
    #Get destination for Dot Locations
    #------------------------------------------------
    pos_analysis_dir = os.path.join(all_analyses_dir, personal, exp_name, analysis_name, pos)
    dot_locations_dir = os.path.join(pos_analysis_dir, 'Dot_Locations')
    #------------------------------------------------
    
    #Get Biggest Jump dst
    #------------------------------------------------
    biggest_jump_dir = os.path.join(dot_locations_dir, 'Biggest_Jump_Histograms')
    os.makedirs(biggest_jump_dir, exist_ok = True)
    biggest_jump_dst = os.path.join(biggest_jump_dir, hyb + '_channel_' + str(channel) + '.png')
    #------------------------------------------------
    
    return biggest_jump_dst
    
    

def get_matlab_detected_dots(tiff_3d_mat_dst, channel, strictness, nbins, threshold, tiff_src, analysis_name):
    
    
    #Get Biggest Jump Histograms dst
    #-------------------------------------------------------------------
    biggest_jump_dst = get_dot_locations_dir(tiff_src, analysis_name, channel)
    #-------------------------------------------------------------------
    
    #Create Dest
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    dest = os.path.join(temp_dir.name, 'locations.mat')
    #dest = 'loc_info.mat'
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    if 'ipykernel' in sys.argv[0]:
        cwd = '/home/nrezaee/test_cronjob_multi_dot'
    else:
        cwd = os.getcwd()
    
    bfmatlab_dir = os.path.join(cwd, 'dot_detection', 'dot_detectors_3d', 'matlab_dot_detection', 'bfmatlab')
    functions_dir = os.path.join(cwd, 'dot_detection', 'dot_detectors_3d', 'matlab_dot_detection')
    print(f'{bfmatlab_dir=}')
    #-------------------------------------------------------------------
    
    
    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    cmd = """  /software/Matlab/R2019a/bin/matlab -r "addpath('{0}');addpath('{1}');biggest_jump('{2}', {3}, {4}, {5}, {6}, '{7}', '{8}'); quit"; """ 
    
    cmd = cmd.format(bfmatlab_dir, functions_dir, tiff_3d_mat_dst, channel, threshold, nbins, strictness, dest, biggest_jump_dst)
    #tiff_src, channel, threshold, nbins, strictness,
    
    os.system(cmd)
    #-------------------------------------------------------------------
    
    dot_analysis = get_dot_analysis(dest)
    print(f'{len(dot_analysis)=}')
    
    return dot_analysis
    
if sys.argv[1] == 'debug':
    tiff_src = 'MMStack_Pos0.ome.tif'
    channel = 0
    threshold = 1000
    nbins = 100
    strictness = 3
    
    dot_analysis = get_matlab_detected_dots(tiff_src, channel, threshold, nbins, strictness)