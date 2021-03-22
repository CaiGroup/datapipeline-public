import numpy as np
from skimage.feature import blob_log
import matplotlib.pyplot as plt
import os

import sys
sys.path.append(os.getcwd())
from load_tiff import tiffy

def get_hist(intense, strictness, hist_png_path):
    num_bins = 100
    plt.figure()
    print(f'{len(intense)=}')
    bins = np.arange(np.min(intense), np.max(intense), (np.max(intense) - np.min(intense))//num_bins)
    y, x, ignore = plt.hist(intense, bins=bins, cumulative=-1)
    thresh = match_thresh_to_diff_stricter(y, x, strictness)
    plt.axvline(x=thresh, color='r')
    print(f'{hist_png_path=}')
    plt.savefig(hist_png_path)
    return y,x, thresh

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
    
def apply_reverse_thresh(dot_analysis, threshold):
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    while (index < len_of_dot_analysis):
        if dot_analysis[1][index] >= threshold:
            dot_analysis[0] = np.delete(dot_analysis[0], index, axis =0)
            dot_analysis[1] = np.delete(dot_analysis[1], index)
            len_of_dot_analysis-=1
            assert len_of_dot_analysis == len(dot_analysis[1])
            index-=1
        indexes.append(index)
        index+=1
    return dot_analysis
    
def remove_unneeded_intensities(intensities, per_remove):
    num_bins = 100
    plt.figure()
    
    print(f'{len(intensities)=}')
    bins = np.arange(np.min(intensities), np.max(intensities), (np.max(intensities) - np.min(intensities))//num_bins)
    y, x, ignore = plt.hist(intensities, bins=bins, cumulative=-1)
    
    bools = y < len(intensities)*per_remove
    i = 0
    while bools[i] == False:
        i+=1
    intensities = np.array(intensities)
    
    threshed = intensities[intensities < x[i]]
    
    return threshed, x[i]

def hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name):
    res = blob_log(tiff_3d, min_sigma =1, max_sigma =2, num_sigma =2, threshold = 0.001)
    points = res[:,:3]

    intensities = []
    for i in range(len(points)):
        intensities.append(tiff_3d[int(points[i,0]), int(points[i,1]), int(points[i,2])])
        
    tiff_split = tiff_src.split(os.sep)
    personal = tiff_split[4]
    exp_name = tiff_split[6]
    hyb = tiff_split[7]
    position = tiff_split[8].split('.ome')[0]
    
    locs_dir = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Dot_Locations')
                        
    if not os.path.exists(locs_dir):
        try:
            os.mkdir(locs_dir)
        except:
            passprint
    
    hist_png_dir = os.path.join(locs_dir, 'Biggest_Jump_Histograms')
    
    if not os.path.exists(hist_png_dir):
        try:
            os.mkdir(hist_png_dir)
        except:
            pass
    
    hist_png_path = os.path.join(hist_png_dir, hyb + '_' + 'Jump.png')
    
    dot_analysis = [points, intensities]
    intensities, reverse_threshold = remove_unneeded_intensities(intensities, per_remove=.01)
    y, x, thresh = get_hist(intensities, strictness, hist_png_path)
    points_threshed, intensities_threshed = apply_thresh(list(dot_analysis), thresh)
    #points_threshed, intensities_threshed = apply_reverse_thresh([points_threshed, intensities_threshed], reverse_threshold)
    return points_threshed, intensities_threshed
    
import sys
if sys.argv[1] == 'debug_jump_helper':
    print(f'{np.version.version=}')
    import tifffile as tf
    
    tiff_src = '/groups/CaiLab/personal/michalp/raw/michal_1/HybCycle_10/MMStack_Pos20.ome.tif'
    tiff_3d = tiffy.load(tiff_src, num_wav=3)[:,0]
    strictness= 5
    analysis_name = 'michal_decoding_top'
    print(f'{tiff_3d.shape=}')
    dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name))
    
    print(f'{dot_analysis[0].shape=}')
    
    
    
    