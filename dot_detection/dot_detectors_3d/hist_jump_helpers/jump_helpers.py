import numpy as np
from skimage.feature import blob_log
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
sys.path.append(os.getcwd())
from load_tiff import tiffy
import numpy as np
import cv2


def save_strictnesses(threshs, cumul_of_dots, thresh, df_dst):
    
    #Get Strictnesses
    #-------------------------------------------------------
    df = pd.DataFrame(list(zip(cumul_of_dots, threshs)),
               columns =['cumulative number of dots', 'threshold'])
    
    index_of_thresh = df[df.threshold == thresh].index[0]
    strictnesses = list(range(index_of_thresh - df.shape[0], index_of_thresh))
    strictnesses.reverse()
    strictnesses = - np.array(strictnesses)
    #-------------------------------------------------------
    
    #Save to csv
    #-------------------------------------------------------
    df['strictness'] = np.array(strictnesses) +1
    df.to_csv(df_dst, index=False)
    #-------------------------------------------------------
    
    return df

def get_hist(intense, strictness, hist_png_path, num_bins):
    
    #Get y's and x's for histogram
    #-------------------------------------------------------
    plt.figure()
    plt.title("Biggest Jump Histogram")
    plt.xlabel("Threshold")
    plt.ylabel("Cumalative Number of Dots")
    bins = np.arange(np.min(intense), np.max(intense), (np.max(intense) - np.min(intense))/num_bins)
    y, x, ignore = plt.hist(intense, bins=bins, cumulative=-1)
    #-------------------------------------------------------
    
    #Get thresh for biggest jump
    #-------------------------------------------------------
    thresh = match_thresh_to_diff_stricter(y, x, strictness)
    #-------------------------------------------------------
    
    #Save strictnesses
    #-------------------------------------------------------
    if hist_png_path != None:
        strict_dst =  os.path.join(os.path.dirname(hist_png_path), 'strictnesses.csv')
        save_strictnesses(x, y, thresh, strict_dst) 
    #-------------------------------------------------------
    
    #Plot line on histogram
    #-------------------------------------------------------
    print(f'{thresh=}')
    plt.axvline(x=thresh, color='r')
    #-------------------------------------------------------
    
    #Only plot if fid not in path
    #-------------------------------------------------------
    if hist_png_path != None:
        if 'fid' not in hist_png_path:
            plt.savefig(hist_png_path)
    #-------------------------------------------------------
    
    return y,x, thresh


def match_thresh_to_diff_stricter(y_hist, x_hist, strictness =1):
    
    #Get index of the biggest diff
    #-------------------------------------------------------
    hist_diffs = get_diff_in_hist(y_hist)
    index_of_max_diff = hist_diffs.index(max(hist_diffs)) + strictness
    print(f'{index_of_max_diff=}')
    #-------------------------------------------------------
    
    #Match index to thresh
    #-------------------------------------------------------
    thresh = x_hist[index_of_max_diff]
    #-------------------------------------------------------

    return thresh

def get_diff_in_hist(y_hist):
    
    #Gets the diff between each hist
    #-------------------------------------------------------
    hist_diffs = []
    for i in range(len(y_hist)-1):
        diff = y_hist[i] - y_hist[i+1]
        hist_diffs.append(diff)
    #-------------------------------------------------------
    
    return hist_diffs

def apply_thresh(dot_analysis, threshold):
    
    #Get indexes to delete
    #-------------------------------------------------------
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    for i in range(len(dot_analysis[1])):
        if dot_analysis[1][i] <= threshold:
            indexes.append(i)
    #-------------------------------------------------------
    
    #Delete indexes
    #-------------------------------------------------------
    dot_analysis[0] = np.delete(dot_analysis[0], indexes, axis =0)
    dot_analysis[1] = np.delete(dot_analysis[1], indexes)
    #-------------------------------------------------------
    return dot_analysis

    
def apply_reverse_thresh(dot_analysis, threshold):
    
    #Apply the threshold in reverse
    #-------------------------------------------------------
    if threshold == None:
        return dot_analysis
    else:
        index = 0
        indexes = []
        len_of_dot_analysis = len(dot_analysis[1])
        for i in range(len(dot_analysis[1])):
            if dot_analysis[1][i] >= threshold:
                indexes.append(i)
        dot_analysis[0] = np.delete(dot_analysis[0], indexes, axis =0)
        dot_analysis[1] = np.delete(dot_analysis[1], indexes)
        return dot_analysis
    #-------------------------------------------------------
    
def remove_unneeded_intensities(intensities, percent_remove, num_bins):
    
    #Get hist_plot
    #-------------------------------------------------------
    plt.figure()
    bins = np.arange(np.min(intensities), np.max(intensities), (np.max(intensities) - np.min(intensities))/num_bins)
    y, x, ignore = plt.hist(intensities, bins=bins, cumulative=-1)
    #-------------------------------------------------------
    
    #Remove the ones that are too high
    #-------------------------------------------------------
    bools = y < len(intensities)*percent_remove
    i = 0
    if any(bools):
        while bools[i] == False:
            i+=1
        intensities = np.array(intensities)
        
        threshed = intensities[intensities < x[i]]
        
        
        return threshed, x[i]
    else:
        return intensities, None
    #-------------------------------------------------------
        
def get_laplacian_params(num_radii, dot_radius, radius_step):
    """
    Get right params when running Laplacian
    """
    
    if num_radii == 2:
        max_radius = dot_radius + radius_step
        min_radius = dot_radius
    elif num_radii == 1:
        min_radius = dot_radius
        max_radius = dot_radius
    elif num_radii > 2:
        max_radius = dot_radius + (radius_step)* num_radii
        min_radius = dot_radius
        
    return num_radii, min_radius, max_radius
    
def get_intensities(points, tiff_3d):
    """
    Trace back intensities of images
    """
    intensities = []
    for i in range(len(points)):
        intensities.append(tiff_3d[int(points[i,0]), int(points[i,1]), int(points[i,2])])
    
    return intensities
    
def get_hist_png_path(tiff_src, analysis_name):

    if analysis_name == None:
        
        #When there is not a place to save the analysis
        #------------------------------------------------------
        hist_png_path = None
        #------------------------------------------------------
    
    else:
        
        #Get the locations dir
        #------------------------------------------------------
        tiff_split = tiff_src.split(os.sep)
        personal = tiff_split[4]
        exp_name = tiff_split[6]
        hyb = tiff_split[7]
        position = tiff_split[8].split('.ome')[0]
        
        locs_dir = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                            analysis_name, position, 'Dot_Locations')
        #------------------------------------------------------
        
        #Have to do this because of parallel processing
        #------------------------------------------------------
        if not os.path.exists(locs_dir):
            try:
                os.mkdir(locs_dir)
            except:
                pass 
        #------------------------------------------------------
        
        hist_png_dir = os.path.join(locs_dir, 'Biggest_Jump_Histograms')
        
        #Have to do this because of parallel processing
        #------------------------------------------------------
        if not os.path.exists(hist_png_dir):
            try:
                os.mkdir(hist_png_dir)
            except:
                pass
        #------------------------------------------------------
        
        #Set path of plotted histograms
        #------------------------------------------------------
        hist_png_path = os.path.join(hist_png_dir, hyb + '_' + 'Jump.png')
        #------------------------------------------------------
    
    return hist_png_path
    

def hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, nbins, threshold, min_sigma, max_sigma, num_sigma, overlap):
    """
    Runs hist jump on 3d img
    """

    #Get points and intensities
    #------------------------------------------------------
    print('Running Blob Log (in Python) with Params: [min sigma = ' + str(min_sigma) + \
                                                ']   [max sigma = ' + str(max_sigma) + \
                                                ']   [num sigma = ' + str(num_sigma) + \
                                                ']   [threshold = ' + str(threshold) + \
                                                ']   [overlap = ' + str(overlap) + ']')
    
    #Make sure Num sigma value is whole number
    #------------------------------------------------------
    if type(num_sigma) == float: 
        assert (num_sigma).is_integer(), 'The num_sigma value must be a whole number.'
    #------------------------------------------------------
    print(f'{tiff_3d.shape=}')
    exclude_border = (0, 2, 2)
    print(f'{exclude_border=}')
    #Run Laplacian of Gaussian Dot Detection
    #------------------------------------------------------
    res = blob_log(tiff_3d, min_sigma = min_sigma, max_sigma = max_sigma, num_sigma = int(num_sigma), 
                    threshold = threshold, overlap=overlap)
    points = res[:,:3]
    intensities = get_intensities(points, tiff_3d)
    #------------------------------------------------------
    
    #Get right format for changing dots
    #------------------------------------------------------
    dot_analysis = [points, intensities]
    #------------------------------------------------------

    #If number of intenities is more than the bins
    #------------------------------------------------------
    if len(intensities) > float(nbins):
    
        #Gets the threshold of dots that are "too bright" and could be false positives
        #------------------------------------------------------
        intensities, reverse_threshold = remove_unneeded_intensities(intensities, percent_remove=.01, num_bins=nbins)
        #------------------------------------------------------
        
        #Get the threshold and applies it to the dots
        #------------------------------------------------------
        hist_png_path = get_hist_png_path(tiff_src, analysis_name)
        y, x, thresh = get_hist(intensities, strictness, hist_png_path, num_bins=nbins)
        points_threshed, intensities_threshed = apply_thresh(list(dot_analysis), thresh)
        #------------------------------------------------------
        
        #Apply the reverse threhold to the dots
        #------------------------------------------------------
        points_threshed, intensities_threshed = apply_reverse_thresh([points_threshed, intensities_threshed], reverse_threshold)
        #------------------------------------------------------
        
        return points_threshed, intensities_threshed
    else:
        return points, intensities
    
    
import sys
if sys.argv[1] == 'debug_jump_helper':
    import tifffile as tf
    
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/linus_data/HybCycle_9/MMStack_Pos0.ome.tif'
    tiff_3d = tiffy.load(tiff_src, num_wav=4,num_z=None)[:,0]
    strictness= 5
    analysis_name = 'linus_decoding'
    print(f'{tiff_3d.shape=}')
    num_bins=100
    dot_radius=1
    radius_step=2
    num_radii= 2
    threshold = .001
    dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, num_bins, dot_radius, threshold, radius_step, num_radii))
    
    print(f'{dot_analysis[0].shape=}')
    
    
    
    