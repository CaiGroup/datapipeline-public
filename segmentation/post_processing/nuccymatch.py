import os
import random
import string
import tifffile
import shutil
import imageio
import numpy as np

def return_in_matched(nuclei_2d, matched_nuclei):
    mask = np.where(np.isin(nuclei_2d, matched_nuclei), nuclei_2d, 0)
    return mask

def match_3d_nuclei_img(nuclei_img, cyto_img, matched_img):
    
    for i in range(nuclei_img.shape[0]):
        nuclei_img[i] = return_in_matched(nuclei_img[i], matched_img)
        
    uniques = np.unique(nuclei_img)
    len(uniques) == len(range(np.max(nuclei_img))) + 1
    new_uniques = list(range(len(uniques)))
    
    for i in range(len(uniques)):
        cyto_img = np.where(cyto_img == uniques[i], \
                                 new_uniques[i], cyto_img)
        nuclei_img = np.where(nuclei_img == uniques[i], \
                                 new_uniques[i], nuclei_img)
        
    return nuclei_img, cyto_img
    
def make_continuous_cyto(cyto_img):
    

    uniques = np.unique(cyto_img)
    len(uniques) == len(range(np.max(cyto_img))) + 1
    new_uniques = list(range(len(uniques)))
    
    for i in range(len(uniques)):
        cyto_img = np.where(cyto_img == uniques[i], \
                                 new_uniques[i], cyto_img)
        
    return cyto_img
    
def run_nuccymatch(post_process_dir, temp_nuclei_path, cyto_2d_src, \
        temp_match_path, area_tol):
    
    nuccy_path = os.path.join(post_process_dir, 'nuccytomatch')
    cmd = 'sh ' + nuccy_path + ' ' + temp_nuclei_path + ' ' + cyto_2d_src + ' ' + temp_match_path + ' ' + str(area_tol)
    print(f'{cmd=}')
    os.system(cmd)
    
            

def get_matched_3d_img(nuclei_3d_src, cyto_2d_src, area_tol, post_process_dir, nuclei_dst = None, cyto_dst = None):

    rand = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) 
    temp_dir = os.path.join('/home/nrezaee/temp', rand)
    print(f'{temp_dir=}')
    os.mkdir(temp_dir)
    
    temp_nuclei_path = os.path.join(temp_dir, 'nuclei_2d.tif')
    temp_match_path  = os.path.join(temp_dir, 'temp')
    temp_match_dst  = os.path.join(temp_dir, 'temp_ncmatch.tif')
    
    nuclei_3d_img = tifffile.imread(nuclei_3d_src)
    nuclei_2d_img = nuclei_3d_img[nuclei_3d_img.shape[0]//2]
    tifffile.imwrite(temp_nuclei_path, nuclei_2d_img)
    
    run_nuccymatch(post_process_dir, temp_nuclei_path, cyto_2d_src, \
            temp_match_path, area_tol)
    
    matched_img = tifffile.imread(temp_match_dst)
    nuclei_labeled_img = matched_img[0,:,:]
    cyto_labeled_img = matched_img[1,:,:]
    
    nuclei_matched_3d, cyto_matched = match_3d_nuclei_img(nuclei_3d_img, cyto_labeled_img, matched_img)
    
    
    
    if nuclei_dst != None:
        tifffile.imwrite(nuclei_dst, nuclei_matched_3d)
    
    if cyto_dst != None:
        print(f'{cyto_labeled_img.shape=}')
        imageio.imwrite(cyto_dst, cyto_matched)
        
    shutil.rmtree(temp_dir)
   

import sys
print('hello')
print(sys.argv)
if sys.argv[1] == 'debug_nuccy':
    print('hi')
    nuclei_3d_src = '/groups/CaiLab/analyses/nrezaee/test1-seg/post_seg_match/MMStack_Pos0/Segmentation/labeled_img.tif'
    cyto_2d_src = '/groups/CaiLab/analyses/nrezaee/test1-seg/post_seg_match/MMStack_Pos0/Segmentation/labeled_cyto_img.tif'
    
    area_tol = 1
    
    post_process_dir = '/home/nrezaee/sandbox/gmic_testing/nuccy_results/'
    
    nuclei_dst = 'nuclei_matched.tif'
    cyto_dst = 'cyto_matched.png'
    
    get_matched_3d_img(nuclei_3d_src, cyto_2d_src, area_tol, \
            post_process_dir, nuclei_dst = nuclei_dst, cyto_dst = cyto_dst)
