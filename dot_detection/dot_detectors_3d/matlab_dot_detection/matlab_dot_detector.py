import tempfile
import os
from scipy.io import loadmat
import numpy as np
import sys

def get_dot_analysis(mat_src):
    mat_info = loadmat(mat_src)
    points = mat_info['dots']
    intensities = mat_info['thresh_ints']
    dot_analysis = [points, np.squeeze(intensities)]
    return dot_analysis

def get_matlab_detected_dots(tiff_src, channel, strictness, nbins, threshold):
    
    
    #Create Dest
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    dest = os.path.join(temp_dir.name, 'locations.mat')
    #dest = 'loc_info.mat'
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    cwd = os.getcwd()
    
    cwd = cwd[cwd.find('/home'):]

    
    bfmatlab_dir = os.path.join(cwd, 'dot_detection', 'dot_detectors_3d', 'matlab_dot_detection', 'bfmatlab')
    functions_dir = os.path.join(cwd, 'dot_detection', 'dot_detectors_3d', 'matlab_dot_detection')
    print(f'{bfmatlab_dir=}')
    #-------------------------------------------------------------------
    
    
    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');addpath('{1}');biggest_jump('{2}', {3}, {4}, {5}, {6}, '{7}'); quit"; """ 
    
    cmd = cmd.format(bfmatlab_dir, functions_dir, tiff_src, channel, threshold, nbins, strictness, dest)
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