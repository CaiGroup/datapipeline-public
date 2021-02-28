import numpy as np
from skimage.feature import blob_log
import matplotlib.pyplot as plt

def get_hist(intense):
    num_bins = 50
    plt.figure()
    print(f'{len(intense)=}')
    bins = np.arange(np.min(intense), np.max(intense), (np.max(intense) - np.min(intense))//num_bins)
    y, x, ignore = plt.hist(intense, bins=bins, cumulative=-1)
    return y,x

def match_thresh_to_diff_stricter(y_hist, x_hist, strictness =1):
    
    hist_diffs = get_diff_in_hist(y_hist)
    index_of_max_diff = hist_diffs.index(max(hist_diffs)) + strictness
    
    print(f'{index_of_max_diff=}')
    thresh = x_hist[index_of_max_diff]

    return thresh

def get_diff_in_hist(y_hist):
    hist_diffs = []
    for i in range(len(y_hist)-1):
        diff = y_hist[i] - y_hist[i+1]
        hist_diffs.append(diff)
        
    return hist_diffs

def apply_thresh(dot_analysis, threshold):
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    while (index < len_of_dot_analysis):
        if dot_analysis[1][index] <= threshold:
            dot_analysis[0] = np.delete(dot_analysis[0], index, axis =0)
            dot_analysis[1] = np.delete(dot_analysis[1], index)
            len_of_dot_analysis-=1
            assert len_of_dot_analysis == len(dot_analysis[1])
            index-=1
        indexes.append(index)
        index+=1
    return dot_analysis

def hist_jump_threshed_3d(tiff_3d, strictness):
    res = blob_log(tiff_3d, min_sigma =1, max_sigma =2, num_sigma =2, threshold = 0.000)
    points = res[:,:3]

    intensities = []
    for i in range(len(points)):
        intensities.append(tiff_3d[int(points[i,0]), int(points[i,1]), int(points[i,2])])
        
    dot_analysis = [points, intensities]
    y, x = get_hist(intensities)
    thresh = match_thresh_to_diff_stricter(y, x, strictness=3)
    points_threshed, intensities_threshed = apply_thresh(list(dot_analysis), thresh)
    return points_threshed, intensities_threshed
    
import sys
if sys.argv[1] == 'debug_jump_helper':
    print(f'{np.version.version=}')
    import tifffile as tf
    
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_1/MMStack_Pos0.ome.tif'
    tiff_3d = tf.imread(tiff_src)[:,0]
    strictness= 5
    
    print(f'{tiff_3d.shape=}')
    dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness))
    
    print(f'{dot_analysis[0].shape=}')
    