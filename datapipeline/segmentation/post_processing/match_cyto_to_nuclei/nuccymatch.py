import os
import random
import string
import tifffile
import shutil
import imageio
import numpy as np

def return_in_matched(nuclei_2d, matched_nuclei):
    
    #Declare where matched
    #------------------------------------------------
    mask = np.where(np.isin(nuclei_2d, matched_nuclei), nuclei_2d, 0)
    #------------------------------------------------
    
    return mask

def match_3d_nuclei_img(nuclei_img, cyto_img, matched_img):
    
    #Only get cells that match in 2d nuclei for whole 3d image
    #------------------------------------------------
    for i in range(nuclei_img.shape[0]):
        nuclei_img[i] = return_in_matched(nuclei_img[i], matched_img)
    #------------------------------------------------
    
    #Make sure the exact cell numbers match up
    #------------------------------------------------
    uniques = np.unique(nuclei_img)
    new_uniques = list(range(len(uniques)))
    for i in range(len(uniques)):
        cyto_img = np.where(cyto_img == uniques[i], \
                                 new_uniques[i], cyto_img)
        nuclei_img = np.where(nuclei_img == uniques[i], \
                                 new_uniques[i], nuclei_img)
    #------------------------------------------------
    
    return nuclei_img, cyto_img
    
    
def run_nuccymatch(post_process_dir, temp_nuclei_path, cyto_2d_src, \
        temp_match_path, area_tol):
    
    #Set command
    #------------------------------------------------
    nuccy_path = os.path.join(post_process_dir, 'match_cyto_to_nuclei', 'nuccytomatch')
    cmd = 'sh ' + nuccy_path + ' ' + temp_nuclei_path + ' ' + cyto_2d_src + ' ' + temp_match_path + ' ' + str(area_tol)
    #------------------------------------------------
    
    #Run command
    #------------------------------------------------
    print(f'{cmd=}')
    os.system(cmd)
    #------------------------------------------------
            

def get_temp_dir():
    
    #Make Temp Dir name
    #------------------------------------------------
    rand = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) 
    temp_dir = os.path.join('/groups/CaiLab/personal/temp/temp_seg', rand)
    print(f'{temp_dir=}')
    #------------------------------------------------
    
    #Make the temp dir
    #------------------------------------------------
    os.mkdir(temp_dir)    
    #------------------------------------------------
    
    return temp_dir
    
    
def get_matched_3d_img(nuclei_3d_src, cyto_2d_src, area_tol, post_process_dir, segment_results_path, nuclei_dst = None, cyto_dst = None):

    temp_dir = get_temp_dir()

    #Declare temp files
    #------------------------------------------------
    temp_nuclei_path = os.path.join(temp_dir, 'nuclei_2d.tif')
    temp_match_path  = os.path.join(temp_dir, 'temp')
    temp_match_dst  = os.path.join(temp_dir, 'temp_ncmatch.tif')
    #------------------------------------------------
    
    #Save nuclei to 2d
    #------------------------------------------------
    nuclei_3d_img = tifffile.imread(nuclei_3d_src)
    nuclei_2d_img = nuclei_3d_img[nuclei_3d_img.shape[0]//2]
    tifffile.imwrite(temp_nuclei_path, nuclei_2d_img)
    #------------------------------------------------
    
    #Nuclei Cyto matching
    #------------------------------------------------
    run_nuccymatch(post_process_dir, temp_nuclei_path, cyto_2d_src, \
            temp_match_path, area_tol)
    #------------------------------------------------
    
    #Read in matched nuclei and cyto
    #------------------------------------------------
    matched_img = tifffile.imread(temp_match_dst)
    nuclei_labeled_img = matched_img[0,:,:]
    cyto_labeled_img = matched_img[1,:,:]
    #------------------------------------------------
    
    
    #Get the matched 3d nuclei and cyto plasm
    #------------------------------------------------
    nuclei_matched_3d, cyto_matched = match_3d_nuclei_img(nuclei_3d_img, cyto_labeled_img, matched_img)
    #------------------------------------------------
    
    #Save the matched nuclei and cytos
    #------------------------------------------------
    if nuclei_dst != None:
        tifffile.imwrite(nuclei_dst, nuclei_matched_3d)
    
    if cyto_dst != None:
        print(f'{cyto_labeled_img.shape=}')
        imageio.imwrite(cyto_dst, cyto_matched)
    #------------------------------------------------
    
    
    #Copy nuclei match to labele_img_post.tif
    #------------------------------------------------
    labeled_img_post_dst = os.path.join(segment_results_path, 'labeled_img_post.tif')
    shutil.copyfile(nuclei_dst, labeled_img_post_dst)
    #------------------------------------------------
        
    #Remove temp dir
    #------------------------------------------------
    shutil.rmtree(temp_dir)
    #------------------------------------------------
   

import sys
print('hello')
print(sys.argv)

if __name__ == '__main__':

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
