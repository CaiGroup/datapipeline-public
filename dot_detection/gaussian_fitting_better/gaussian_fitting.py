import os 
import numpy as np
from scipy.io import loadmat, savemat
import tempfile


def get_gaussian_fitted_dots(tiff_src, channel,points):
    
    breakpoint()
    #Save Points to path
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    print(temp_dir.name)
    
    points_saved_path = os.path.join(temp_dir.name, 'points.mat')
    #points_saved_path = 'saved_locs.mat'
    savemat(points_saved_path, {'points': points})
    #-------------------------------------------------------------------
    
    #Get temp dir
    #-------------------------------------------------------------------
    #temp_dir = tempfile.TemporaryDirectory()
    
    gauss_fitted_dots_path = os.path.join(temp_dir.name, 'gauss_points.mat')
    #gauss_fitted_dots_path ='gauss_points.mat'
    
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    cwd = os.getcwd()
    
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    
    bfmatlab_dir = os.path.join(cwd,'dot_detection', 'gaussian_fitting_better',  'bfmatlab')
    helpers_dir = os.path.join(cwd,'dot_detection', 'gaussian_fitting_better', 'helpers')
    #-------------------------------------------------------------------
    
    print('=========================')
    #Create Matlab Command
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');addpath('{1}'); getgaussian_wrap('{2}', {3}, '{4}', '{5}'); quit"; """ 
    
    gauss_fitted_dots_path ='gauss_points.mat'
    cmd = cmd.format(bfmatlab_dir, helpers_dir, tiff_src, channel, points_saved_path, gauss_fitted_dots_path)
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
    mat_results = loadmat(gauss_fitted_dots_path)
    gauss_points = mat_results['gaussPoints']
    gauss_ints = mat_results['gaussInt']
    
    gauss_dot_analysis = [gauss_points, gauss_ints]
    #-------------------------------------------------------------------
    
    return gauss_dot_analysis
    
    
# tiff_src = 'MMStack_Pos0.ome.tif'
# channel = 1
# points = np.random.randint(8,10, size=(100, 3))

# gauss_dot_analysis = get_gaussian_fitted_dots(tiff_src, channel, points)

# print(f'{len(gauss_dot_analysis)=}')
# print(f'{gauss_dot_analysis[0].shape=}')
# print(f'{gauss_dot_analysis[1].shape=}')