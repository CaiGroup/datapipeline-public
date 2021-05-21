import subprocess
import os
from shutil import copyfile
import shutil
import tifffile
import numpy as np
import sys
import random 
import string
import glob
import tifffile as tf

print(1)
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from segmentation.cellpose_segment.helpers import cellpose_segment_funcs
from segmentation.cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs
from segmentation.post_processing.get_cyto_labeled_img import get_labeled_cyto_cellpose

from segmentation.post_processing.nuccymatch import get_matched_3d_img

def make_distance_between_cells(label_img_src, dist_between_nuclei, post_process_dir):
    
    #Specify directory and files
    #-------------------------------------------------------------
    label_img_dir = os.path.dirname(label_img_src)
    nuctouchresize_file_path = os.path.join(post_process_dir, 'nuctouchresize')
    #-------------------------------------------------------------
    
    #Run the distance maker
    #-------------------------------------------------------------
    print("Making Distance Between Cells")
    subprocess.call(['sh', nuctouchresize_file_path, label_img_src, str(dist_between_nuclei)])
    #-------------------------------------------------------------
    
    #Return Labeled image location
    #-------------------------------------------------------------
    label_img_src = os.path.join(label_img_dir, 'labeled_img_r' + str(dist_between_nuclei) + '.tif')
    print(f'{label_img_src=}')
    return label_img_src
    #-------------------------------------------------------------
    
def delete_edges(label_img_src, edge_delete_dist, post_process_dir):

    #Specify directory and files
    #-------------------------------------------------------------
    label_img_dir = os.path.dirname(label_img_src)
    nucboundzap_file_path = os.path.join(post_process_dir, 'nucboundzap')    
    #-------------------------------------------------------------
    
    #Run the edge deleter
    #-------------------------------------------------------------
    print("Deleting Edges")
    subprocess.call(['sh', nucboundzap_file_path, label_img_src, str(edge_delete_dist)])
    #-------------------------------------------------------------
    
    #Return dst of labeled image
    #-------------------------------------------------------------
    label_img_src = os.path.join(label_img_dir, label_img_src.replace('.tif', '') + '_bzap_d' + str(edge_delete_dist) + '.tif')
    print(f'{label_img_src=}')
    return label_img_src
    #-------------------------------------------------------------

def get_debug():
    
    #Get Past images to save time
    #-------------------------------------------------------------
    labeled_img_path ='/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_img_r12_bzap_d8.tif'
    labeled_cyto_path = '/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_cyto_img.tif'
    #-------------------------------------------------------------
    
    return labeled_img_path, labeled_cyto_path
    
    
def get_labeled_imgs(segment_results_path, tiff_for_segment, bool_cyto_match, cyto_channel_num, get_nuclei_img, \
                     get_cyto_img, num_wav, nuclei_radius, num_z):
    
    #Get the cytoplasm labeled image if bool cyto match is true
    #-------------------------------------------------------------
    if bool_cyto_match == True:
        labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
        label_img = get_labeled_img_cellpose(tiff_for_segment, dst = labeled_img_path, num_wav = num_wav)
        
        labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
        labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, cyto_channel = cyto_channel_num, num_wav = num_wav)
    #-------------------------------------------------------------
    
    
    else:
            
        #Ignore if you already have the labeled image
        #-------------------------------------------------------------
        if 'Labeled_Images' in tiff_for_segment:
            labeled_img_path = tiff_for_segment
            labeled_cyto_path = None
        #-------------------------------------------------------------
        
        else:
            
            # Get nuclei labeled image if true
            #-------------------------------------------------------------
            if get_nuclei_img == True:
                labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
                label_img = get_labeled_img_cellpose(tiff_for_segment, dst = labeled_img_path, num_wav = num_wav, nuclei_radius=nuclei_radius)
            else:
                labeled_img_path = None
            #-------------------------------------------------------------
            
            
            #Get Cytoplasm labeled image if true
            #-------------------------------------------------------------
            if get_cyto_img == True:
                labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
                labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, cyto_channel = cyto_channel_num, num_wav = num_wav)
            else:
                labeled_cyto_path = None
            #-------------------------------------------------------------

    return labeled_img_path, labeled_cyto_path
    
def make_2d_into_3d(tiff_2d, num_z=20):
    
    #Stack the same z on top of each other
    #-------------------------------------------------------------
    tiff_3d = []
    for i in range(num_z):
        tiff_3d.append(tiff_2d)
    tiff_3d = np.array(tiff_3d).astype(np.int16)
    #-------------------------------------------------------------
    return tiff_3d
    
def get_tiff_for_segment(tiff_dir, position, num_z):
    
    #Get all directories
    #-------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    all_dirs = glob.glob(glob_me)
    print(f'{all_dirs=}')
    #-------------------------------------------------------------
    
    #Check to see if segmentation is specified
    #-------------------------------------------------------------
    bool_seg_dir = [('segmentation' == a_dir.rsplit('/', 1)[-1]) for a_dir in all_dirs]
    print(f'{bool_seg_dir=}')
    bool_labeled_img_dir = [('Labeled_Images' == a_dir.rsplit('/', 1)[-1]) for a_dir in all_dirs]
    print(f'{bool_seg_dir=}')
    #-------------------------------------------------------------

    #If labeled image is already specified
    #-------------------------------------------------------------
    if any(bool_labeled_img_dir):
        tiff_for_segment = os.path.join(tiff_dir, 'Labeled_Images', position)
        tiff = tf.imread(tiff_for_segment)
        if len(tiff.shape) == 3:
            pass
        elif len(tiff.shape) ==2:
            tiff_3d = make_2d_into_3d(tiff, num_z)
            tiff_for_segment = tiff_for_segment.replace('.ome.', '2d_stacked.ome.')
            tf.imwrite(tiff_for_segment, tiff_3d)
        else:
            raise Exception("The Labeled Image has to be 2d or 3d.")
    #-------------------------------------------------------------
    
    #If tiff to segment is already specified
    #-------------------------------------------------------------
    elif any(bool_seg_dir):
        tiff_for_segment = glob.glob(os.path.join(tiff_dir, 'segmentation', position))[0]
    #-------------------------------------------------------------
    
    #Get the first tiff
    #-------------------------------------------------------------
    else:
        sorted_hybs = get_and_sort_hybs(glob_me)
        assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"
        
        tiff_for_segment = os.path.join(sorted_hybs[0], position)
    #-------------------------------------------------------------
        
    print(f'{tiff_for_segment=}')
    return tiff_for_segment
        
def post_process(edge_delete_dist, dist_between_nuclei, label_img_src, labeled_cyto_path, label_img_dst):
    
    
    #Get Post Process Directory
    #-------------------------------------------------------------
    cwd = os.getcwd()
    post_process_dir = os.path.join(cwd, 'segmentation/post_processing')
    #-------------------------------------------------------------
    
    #Make distance between nuclei
    #-------------------------------------------------------------
    if float(dist_between_nuclei)==0:
        pass
    else:
        label_img_src = make_distance_between_cells(label_img_src, int(float(dist_between_nuclei)), post_process_dir)
    #-------------------------------------------------------------
    
    #Delete nuclei on edges
    #-------------------------------------------------------------
    if float(edge_delete_dist)  == 0:
        pass
    else:
        label_img_src = delete_edges(label_img_src, int(float(edge_delete_dist)), post_process_dir)
    #-------------------------------------------------------------
    
    
    #Put labeled image in destination 
    # I have to put the try except statement in for parallel processing
    #-------------------------------------------------------------
    try:
        print(f'{label_img_dst=}')
        copyfile(label_img_src, label_img_dst)
    except OSError:
        print("The labeled image was already transfferred")
    #-------------------------------------------------------------
    
        
    
def save_labeled_img(tiff_dir, segment_results_path, position, edge_delete_dist, dist_between_nuclei, bool_cyto_match, \
        area_tol, cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, num_z, debug = False):
    
    #Get Post Process Dir and tiff
    #-------------------------------------------------------------
    cwd = os.getcwd()
    post_process_dir = os.path.join(cwd, 'segmentation/post_processing')
    
    tiff_for_segment = get_tiff_for_segment(tiff_dir, position, num_z)
    #-------------------------------------------------------------
    
    
    # Get labeled images with debug or real
    #-------------------------------------------------------------
    print("Getting Labeled Images")
    if debug == True:
        labeled_img_path, labeled_cyto_path = get_debug()
        
    else:
        labeled_img_path, labeled_cyto_path = get_labeled_imgs(segment_results_path, tiff_for_segment, bool_cyto_match, \
                                                cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, \
                                                num_z)
    #-------------------------------------------------------------
    
    
    # For the case when you already have a labeled image
    #-------------------------------------------------------------
    if labeled_img_path != None:
        label_img_post_processed_dst = os.path.join(segment_results_path, 'labeled_img_post.tif')
        post_process(edge_delete_dist, dist_between_nuclei, labeled_img_path, labeled_cyto_path, label_img_post_processed_dst)
        labeled_img_path = label_img_post_processed_dst
    #-------------------------------------------------------------
    
    # Match the nuclei and cytoplasm
    #-------------------------------------------------------------
    if bool_cyto_match:
        print("Running Nuccy Match")
        nuclei_dst = os.path.join(segment_results_path, 'nuclei_labeled_img_matched.tif')
        cyto_dst = os.path.join(segment_results_path, 'cyto_labeled_img_matched.tif')
        get_matched_3d_img(labeled_img_path, labeled_cyto_path, area_tol, post_process_dir, nuclei_dst, cyto_dst)
        
        return nuclei_dst
    
    #or dont match    
    else:
        
        if labeled_img_path == None:
            return labeled_cyto_path
        else:
            return labeled_img_path
    #-------------------------------------------------------------

    
if sys.argv[1] == 'debug_post':
    print('=---------------------------------------')
    tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/2021_0512_mouse_hydrogel/'
    segment_results_path = '/home/nrezaee/temp2'
    position  = 'MMStack_Pos0.ome.tif'
    edge = 0
    dist = 0
    bool_cyto_match = False
    area_tol = 1
    debug = False
    cyto_channel_num = 1
    get_nuc = True
    get_cyto = False
    num_z=3
    num_wav=4
    nuclei_radius = 0
    save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol, \
                cyto_channel_num, get_nuc, get_cyto, num_wav, nuclei_radius, num_z, debug=debug)

    
    
    
    
    
    
        