import tifffile as tf
import os 
import matplotlib.pyplot as plt
import cv2
import numpy as np
from skimage import feature

import sys
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from helpers.reorder_hybs import get_and_sort_hybs
from load_tiff import tiffy

def get_img_3d_edges(img_3d):
    print('Getting Edges')
    edges_3d = []
    for i in range(len(img_3d)):
        edges_3d.append(feature.canny(img_3d[i]))
    edges_3d = np.array(edges_3d)
    return edges_3d

    
def plot_labeled_img_edges_on_tiff(tiff_src, labeled_img_src, dst_dir, num_wav):
    
    #Read Dapi tiff and labeled img
    #---------------------------------------------
    dapi_channel = -1
    tiff = tiffy.load(tiff_src, num_wav)
    dapi_3d = tiff[:,-1]

    labeled_img = tf.imread(labeled_img_src)
    #---------------------------------------------
    
    #Get Edges of Labeled Img
    #---------------------------------------------
    edges_3d = get_img_3d_edges(labeled_img)
    #edges_3d = labeled_img
    #---------------------------------------------
    
    #Add edges and plot image
    #---------------------------------------------
    dapi_3d = dapi_3d + edges_3d*300
    for i in range(len(dapi_3d)):
        dst_png = os.path.join(dst_dir, 'Z_slice_' + str(i) + '.png')
        plt.figure(figsize=(20,20))
        plt.imshow(dapi_3d[i]*10, cmap='gray')
        plt.savefig(dst_png)
        print(f'{dst_png=}')
    #---------------------------------------------
    
def get_label_img_visuals(label_src, tiff_dir, position, num_wav):

    #Get Tiff for Segmentation
    #-----------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    sorted_hybs = get_and_sort_hybs(glob_me)
    assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"
    tiff_for_segment = os.path.join(sorted_hybs[0], position)
    print(f'{tiff_for_segment=}')    #-----------------------------------------------------------------

    #Set Directory for labeled images
    #-----------------------------------------------------------------
    dir_dst  = os.path.join(os.path.dirname(label_src), 'Labeled_Img_Visuals')
    if not os.path.exists(dir_dst):
        os.makedirs(dir_dst)
    #-----------------------------------------------------------------
    
    #Plot Labeled Image edges on DAPI
    #-----------------------------------------------------------------
    plot_labeled_img_edges_on_tiff(tiff_for_segment, label_src, dir_dst, num_wav)
    #-----------------------------------------------------------------
    
    
        
if sys.argv[1] == 'debug_show_visuals':
    label_src = '/groups/CaiLab/analyses/nrezaee/test1-seg/post_seg/MMStack_Pos0/Segmentation/nuclei_labeled_img_matched.tif'
    tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1-seg'
    position = 'MMStack_Pos0.ome.tif'
    num_wav = 2
    get_label_img_visuals(label_src, tiff_dir, position, num_wav)
    
    
    