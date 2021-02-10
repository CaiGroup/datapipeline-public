import tifffile
import os 
import matplotlib.pyplot as plt
import cv2
import numpy as np

import sys
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from helpers.reorder_hybs import get_and_sort_hybs
from load_tiff import tiffy

def get_labeled_img_red(label_img):  
    if type(label_img)== list:
        label_img = np.array(label_img)
    label_img_rgb = [] 
    
    print(f'{label_img.shape=}')
    for i in range(label_img.shape[0]):
        label_img_z = cv2.cvtColor(label_img[i].astype(np.uint8), cv2.COLOR_GRAY2RGB)
        label_img_z[:,:,1] = 0
        label_img_z[:,:,2] = 0
      
        label_img_rgb.append(label_img_z)
        
    label_img_rgb = np.array(label_img_rgb)
    return label_img_rgb
    
def get_label_img_visuals(label_src, tiff_dir, position):

    #Get Tiff for Segmentation
    #-----------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    sorted_hybs = get_and_sort_hybs(glob_me)
    assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"

    tiff_for_segment = os.path.join(sorted_hybs[0], position)
    print(f'{tiff_for_segment=}')
    tiff = tiffy.load(tiff_for_segment)
    #-----------------------------------------------------------------

    dir_dst  = os.path.join(os.path.dirname(label_src), 'Labeled_Img_Visuals')
    if not os.path.exists(dir_dst):
        os.makedirs(dir_dst)
    
    print('Labeled Image visuals source:', label_src)
    label_img = tifffile.imread(label_src)
    label_img = get_labeled_img_red(label_img)
   
    print(f'{tiff.shape=}')
    for z in range(tiff.shape[0]):
        print(f'{z=}')
        img_z_dst = os.path.join(dir_dst, 'labeled_img_' + str(z) + 'z.png')
        plt.figure()
        plt.imshow(label_img[z]*100)
        plt.imshow(tiff[z, -1], alpha=0.5)
        plt.savefig(img_z_dst)
        
# label_src = '/groups/CaiLab/analyses/nrezaee/test1-seg/post_seg/MMStack_Pos0/Segmentation/nuclei_labeled_img_matched.tif'
# tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1-seg'
# position = 'MMStack_Pos0.ome.tif'
# get_label_img_visuals(label_src, tiff_dir, position)