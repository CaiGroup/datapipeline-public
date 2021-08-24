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

def get_matlab_detected_dots(tiff_src, channel, strictness, nbins, threshold):
    
    
    #Create Dest
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    dest = os.path.join(temp_dir.name, 'locations.mat')
    #dest = 'loc_info.mat'
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    folder = os.path.dirname(__file__)

    bfmatlab_dir = os.path.join(folder, 'bfmatlab')
    functions_dir = folder
    print(f'{bfmatlab_dir=}')
    #-------------------------------------------------------------------
    
    
    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    cmd = """  /software/Matlab/R2019a/bin/matlab -r "addpath('{0}');addpath('{1}');biggest_jump('{2}', {3}, {4}, {5}, {6}, '{7}'); quit"; """ 
    
    cmd = cmd.format(bfmatlab_dir, functions_dir, tiff_src, channel, threshold, nbins, strictness, dest)
    #tiff_src, channel, threshold, nbins, strictness,
    
    os.system(cmd)
    #-------------------------------------------------------------------
    
    dot_analysis = get_dot_analysis(dest)
    print(f'{len(dot_analysis)=}')
    
    return dot_analysis


if __name__ == '__main__':

    if sys.argv[1] == 'debug':
        tiff_src = 'MMStack_Pos0.ome.tif'
        channel = 0
        threshold = 1000
        nbins = 100
        strictness = 3

        dot_analysis = get_matlab_detected_dots(tiff_src, channel, threshold, nbins, strictness)