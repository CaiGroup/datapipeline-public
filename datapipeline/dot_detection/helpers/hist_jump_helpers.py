from __future__ import annotations
import numpy as np
import imageio
import skimage
import tifffile
import os
import glob
from typing import Tuple
import numpy as np
from scipy import ndimage
import scipy.ndimage
from skimage.exposure import rescale_intensity
from skimage.feature import blob_log
from skimage.filters import difference_of_gaussians
from scipy.ndimage._ni_support import _normalize_sequence
import scipy.ndimage as ndi
import cv2
import warnings
import json
import warnings
import math
import matplotlib.pyplot as plt
import tempfile
from scipy.io import loadmat

from dot_detection.helpers.add_z import add_z_col
from dot_detection.helpers.threshold import apply_thresh
from dot_detection.helpers.compile_dots import add_to_dots_in_channel

def match_thresh_to_diff_stricter(y_hist, x_hist, strictness =1):
    
    hist_diffs = get_diff_in_hist(y_hist)
    index_of_max_diff = hist_diffs.index(max(hist_diffs)) + strictness
    
    if index_of_max_diff >= len(x_hist) - 2:
        index_of_max_diff = len(x_hist) - 2
    
    thresh = x_hist[index_of_max_diff]

    return thresh

def rolling_ball_filter(
    data: np.ndarray,
    ball_radius: float,
    spacing: Optional[Union[int, Sequence]] = None,
    top: bool = False,
) -> np.ndarray:
    """Rolling ball filter implemented with morphology operations.

    This implemetation is very similar to that in ImageJ and uses a top hat
    transform with a ball shaped structuring element with Image smoothing. Output
    is almost exactly as in ImageJ.

    Args:
        data: Image data (assumed to be on a regular grid).
        ball_radius: The radius of the ball to roll.
        spacing: The spacing of the image data.
        top: Whether to roll the ball on the top or bottom of the data.

    Returns:
        Data with background subtracted.
    """
    ndim = data.ndim
    if spacing is None:
        spacing = np.ones(ndim)
    else:
        spacing = _normalize_sequence(spacing, ndim)

    kernel = np.ones((3, 3), np.float64) / (3 * 3)
    _data = cv2.filter2D(data, -1, kernel)

    radius = np.asarray(_normalize_sequence(ball_radius, ndim))
    mesh = np.array(
        np.meshgrid(
            *[np.arange(-r, r + s, s) for r, s in zip(radius, spacing)],  # type: ignore
            indexing="ij"
        )
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        structure = 2 * np.sqrt(
            1 - ((mesh / radius.reshape(-1, *((1,) * ndim))) ** 2).sum(0)
        )
    structure[~np.isfinite(structure)] = 0
    if not top:
        # ndi.white_tophat(y, structure=structure, output=background)
        background = ndi.grey_erosion(_data, structure=structure)
        background = ndi.grey_dilation(background, structure=structure)
    else:
        # ndi.black_tophat(y, structure=structure, output=background)
        background = ndi.grey_dilation(_data, structure=structure)
        background = ndi.grey_erosion(background, structure=structure)

    data = data.astype("float64") - background.astype("float64")
    b = data < 0
    data[b] = 0

    return data


def get_diff_in_hist(y_hist):
    hist_diffs = []
    for i in range(len(y_hist)-1):
        diff = y_hist[i] - y_hist[i+1]
        hist_diffs.append(diff)
        
    return hist_diffs

def match_thresh_to_diff(y_hist, x_hist):
    
    hist_diffs = get_diff_in_hist(y_hist)
    index_of_max_diff = hist_diffs.index(max(hist_diffs))
    
    thresh = x_hist[index_of_max_diff]

    return thresh
    
def get_hist(intense):
    num_bins = 100
    plt.figure(figsize=(10,10))
    bins = np.arange(np.min(intense), np.max(intense), (np.max(intense) - np.min(intense))//num_bins)
    y, x, ignore = plt.hist(intense, bins=bins, cumulative=-1)
    return y,x


def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel  = tuple(np.array(tiff_2d.shape)//num_tiles)
    #print(f'{blur_kernel=}')
    blurry_img = cv2.blur(tiff_2d,blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return tiff_2d

    
def blur_back_subtract_3d(tiff, num_tiles):
    
    print(f'{tiff.shape=}')
    for i in range(tiff.shape[0]):
        tiff[i,:,:] = blur_back_subtract(tiff[i,:,:], num_tiles)
    return tiff

def tophat_3d(tiff_3d):
    kernel = np.full((2,2), 100)
    for i in range(tiff_3d.shape[0]):
        tiff_3d[i] = cv2.morphologyEx(tiff_3d[i], cv2.MORPH_TOPHAT, kernel) 
        
    return tiff_3d
    


def process_3d(tiff_3d, tile_split=5):
    
    tiff_3d = blur_back_subtract_3d(tiff_3d, tile_split)
    
    tiff_3d = tophat_3d(tiff_3d)
    #tiff_3d = blur_back_subtract_3d(tiff_3d, num_tiles=2)
    
    print(' Image Processing Done!')
    return tiff_3d

def find_dots(chan_img: np.ndimage) -> Tuple[np.ndarray, np.ndarray, int]:

    # Corresponds to a dot radius of sqrt(2)
    sigma = 2

    # Background subtraction with rolling ball radius of 3
    subtracted = rolling_ball_filter(chan_img, 3, spacing=None, top=False)

    # Scaled Laplacian over which blob_log maximizes to find dots
    laplacian = -ndimage.gaussian_laplace(subtracted, sigma) * sigma ** 2
    positive_laplacian = laplacian[laplacian > 0]

    # Mean of positive Laplacian values plus half of standard deviation has been
    # observed to be a good base threshold for capturing dots
    mean = np.mean(positive_laplacian)
    stdev = np.std(positive_laplacian)
    capture_threshold = np.round(mean + stdev / 2)

    # Run LoG dot finder
    log_result = blob_log(
        subtracted,
        min_sigma=sigma,
        max_sigma=sigma,
        num_sigma=1,
        threshold=capture_threshold,
    )

    points = log_result[:, :2].astype(np.int64)
    intensities = chan_img.transpose()[points[:, 1], points[:, 0]]


    return points, intensities #, suggested_threshold



def find_dots_3d(tiff_3d, min_sigma=2, max_sigma=2, sigma_std =1, overlap=.2):
    #intens_img = get_tile_norms(tiff_3d, intens=True)
    #tiff_3d = blur_back_subtract_3d(tiff_3d, num_tiles=2)
    #tiff_3d_norm = cv2.normalize(tiff_3d, None, 0, 10, norm_type=cv2.NORM_MINMAX).astype(np.int16)
    dots_in_channel = None
    for z in range(tiff_3d.shape[0]):
        print(' ' + str(z), end='')
        tiff_2d = tiff_3d[z, :, :]

        #Get dots from 2d image
        #---------------------------------------------------------------------
        dot_analysis = list(find_dots(tiff_2d))
        #---------------------------------------------------------------------

        #Add Z column to dot locations
        #---------------------------------------------------------------------
        dot_analysis = add_z_col(dot_analysis, z)
        #---------------------------------------------------------------------

        #Switch [y, x, z] to [x, y, z]
        #---------------------------------------------------------------------
        dot_analysis[0][:,[0,1]] = dot_analysis[0][:,[1,0]]
        #---------------------------------------------------------------------
        
        dots_in_channel = add_to_dots_in_channel(dots_in_channel, dot_analysis)

    return dots_in_channel[0], dots_in_channel[1]
    
def get_hist_threshed_dots(tiff_3d, strictness=10):
        #Process and get dots on image
    processed_img_3d = process_3d(tiff_3d, tile_split=90)
    
    dot_analysis = find_dots_3d(processed_img_3d)
    
    assert len(dot_analysis[1]) >0
    # Get histogram
    intensities = dot_analysis[1]
    
    y, x = get_hist(intensities)
    
    # Threshold dots
    thresh = match_thresh_to_diff_stricter(y, x, strictness=strictness)
    print(f'{thresh=}')
    print("Applying thresh")
    points, intense = apply_thresh(list(dot_analysis), thresh)
    
    return points, intense