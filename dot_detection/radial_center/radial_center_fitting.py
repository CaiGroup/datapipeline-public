import os 
#import tempfile
import numpy as np
from scipy.io import loadmat, savemat
import tempfile
import tempfile


def get_radial_centered_dots(tiff_src, channel, points):
    
    
    #Save Points to path
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    print(temp_dir.name)
    
    points_saved_path = os.path.join(temp_dir.name, 'points.mat')
    #points_saved_path = 'saved_locs.mat'
    
    #points[:, [0, 1]] = points[:, [1, 0]] 
    print(f'{points[:10]=}')
    
    savemat(points_saved_path, {'points': points})
    #-------------------------------------------------------------------
    
    #Get temp dir
    #-------------------------------------------------------------------
    rad_dots_path = os.path.join(temp_dir.name, 'rad_points.mat')
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    cwd = os.getcwd()
    
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    
    rad_dir = os.path.join(cwd, 'dot_detection', 'radial_center')
    
    bfmatlab_dir = os.path.join(rad_dir, 'bfmatlab')
    helpers_dir = os.path.join(rad_dir, 'helpers')
    #-------------------------------------------------------------------
    
    print('=========================')
    #Create Matlab Command
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');addpath('{1}'); super_wrap_wrap('{2}', {3}, '{4}', '{5}'); quit"; """ 
    
    gauss_fitted_dots_path ='gauss_points.mat'
    cmd = cmd.format(bfmatlab_dir, helpers_dir, tiff_src, channel, points_saved_path, rad_dots_path)
    #-------------------------------------------------------------------
    
    
    #Run Matlab Command
    #-------------------------------------------------------------------
    print('Running Command')
    
    print(f'{cmd=}')
    os.system(cmd)
 
    print('After command')
    #-------------------------------------------------------------------
    
    
    #Load Results from Matlab
    #-------------------------------------------------------------------
    mat_results = loadmat(rad_dots_path)
    rad_points = mat_results['radPoints']
            

    #rad_points[:, [1, 0]] = rad_points[:, [0, 1]] 
    print(f'{rad_points[:10]=}')
    
    rad_ints = mat_results['radInt']
    
    
    
    rad_dot_analysis = [rad_points, rad_ints]
    #-------------------------------------------------------------------
    
    return rad_dot_analysis
    
    
# tiff_src = '/groups/CaiLab/personal/nrezaee/raw/test1-big/HybCycle_50/MMStack_Pos0.ome.tif';
# channel = 0
# points=np.array([[  44,  676,    10],
#       [ 124, 1919,    1],
#       [ 384,  918,    1],
#       [ 919,  178,    1],
#       [1803, 1462,    1],
#       [1662,  922,    2],
#       [ 124, 1919,    3],
#       [ 705,  882,    3],
#       [ 716, 1063,    3],
#       [ 736, 1020,    3]], dtype=np.uint16)
       

# gauss_dot_analysis = get_radial_centered_dots(tiff_src, channel, points)

# print(f'{len(gauss_dot_analysis)=}')
# print(f'{gauss_dot_analysis[0].shape=}')
# print(f'{gauss_dot_analysis[1].shape=}')

