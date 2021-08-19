import os 
import numpy as np
from scipy.io import loadmat, savemat
from scipy.optimize import least_squares
from webfish_tools.util import pil_imread
import tempfile


def get_region_around(im, center, size, normalize=True, edge='raise'):
    lower_bounds = np.array(center) - size // 2
    upper_bounds = np.array(center) + size // 2 + 1

    if any(lower_bounds < 0) or any(upper_bounds > im.shape[-1]):
        if edge == 'raise':
            raise IndexError(f'Center {center} too close to edge to extract size {size} region')
        elif edge == 'return':
            lower_bounds = np.maximum(lower_bounds, 0)
            upper_bounds = np.minimum(upper_bounds, im.shape[-1])

    region = im[lower_bounds[0]:upper_bounds[0], lower_bounds[1]:upper_bounds[1]]

    if normalize:
        return region / region.max()
    else:
        return region

def get_gaussian_fitted_dots_python(tiff_src, channel, points, region_size=7):

    if region_size % 2 == 0:
        region_size += 1

    image = pil_imread(tiff_src)[channel]

    def _gaussian_fit(params, grid, imdata, sigmas):
        """
        Evaluate a gaussian with parameters params (center, sigma, magnitude)
        on grid and return pixelwise residuals with imdata
        """

        center_x, center_y, mag = params
        sigma_x, sigma_y = sigmas

        X, Y = grid
        exp = (X - center_x) ** 2 / (2 * sigma_x ** 2) + (Y - center_y) ** 2 / (2 * sigma_y ** 2)

        return np.ravel((mag * np.exp(-exp)) - imdata)

    grid = np.mgrid[0:region_size, 0:region_size]
    opts = []
    mags = []

    for cand in points:
        z, x, y = cand
        zint = int(z)
        xint, yint = int(x), int(y)

        mag = image[zint-1, xint, yint]
        mags.append(mag)

        try:
            im_data = get_region_around(image[zint-1], [xint, yint], region_size, )
        except IndexError:
            opts.append(cand)
            continue

        loc_2d = least_squares(
            _gaussian_fit,
            x0=(5, 5, mag),
            x_scale=(1, 1, 100),
            xtol=1e-2,
            args=(grid, im_data, (2, 2)),
            method='lm'
        ).x[:2] + [x, y] - region_size // 2

        loc_3d = np.array([z] + list(loc_2d))
        opts.append(loc_3d)

    return [np.array(opts), np.array(mags)]


def get_gaussian_fitted_dots(tiff_src, channel,points):
    
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