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
import tempfile

sys.path.insert(0, os.getcwd())

#Import Functions for getting labeled images
#-------------------------------------------------------------
from ..cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from ..post_processing.get_cyto_labeled_img import get_labeled_cyto_cellpose
#-------------------------------------------------------------

#Sort Hybs to get the first Hyb Cycle
#-------------------------------------------------------------
from ..cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs
#-------------------------------------------------------------

#Function for matching cytoplasm and nucleus
#-------------------------------------------------------------
from ..post_processing.match_cyto_to_nuclei.nuccymatch import get_matched_3d_img
#-------------------------------------------------------------

#Edge deletion and distance between cells
#-------------------------------------------------------------
from ..post_processing.edge_deletion.get_edge_deletion import delete_edges
from ..post_processing.distance_between_cells.get_distance_between_cells import make_distance_between_cells
#-------------------------------------------------------------

def switch_low_z_to_right_shape(labeled_src):
    label_img = tf.imread(labeled_src)
    
    label_img = np.swapaxes(label_img, 0, 2)
    label_img = np.swapaxes(label_img, 1, 2)
    
    tf.imwrite(labeled_src, label_img)
    return label_img
    
def get_debug():
    
    #Get Past images to save time
    #-------------------------------------------------------------
    labeled_img_path ='/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_img_r12_bzap_d8.tif'
    labeled_cyto_path = '/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_cyto_img.tif'
    #-------------------------------------------------------------
    
    return labeled_img_path, labeled_cyto_path
    
    
    
def get_labeled_imgs(raw_dir, position, segment_results_path, tiff_for_segment, bool_cyto_match, cyto_channel_num, get_nuclei_img, 
                     get_cyto_img, num_wav, nuclei_radius, num_z, flow_threshold, cell_prob_threshold, nuclei_channel_num,
                     cyto_flow_threshold, cyto_cell_prob_threshold, cyto_radius):
    
    print(f'{tiff_for_segment=}')
    #Get the cytoplasm labeled image if bool cyto match is true
    #-------------------------------------------------------------
    if bool_cyto_match == True:
        
        #Ignore if you already have the labeled image
        #-------------------------------------------------------------
        if 'Labeled_Images' in tiff_for_segment:
            print('Using premade Labeled Image for Nuclei')
            labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
            copyfile(tiff_for_segment, labeled_img_path)
        #-------------------------------------------------------------
        
        #Get Labeled Image with Cellpose
        #-------------------------------------------------------------
        else:
            labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
            label_img = get_labeled_img_cellpose(tiff_for_segment, dst = labeled_img_path, num_wav = num_wav, nuclei_channel_num = nuclei_channel_num, num_z = num_z)
        
        #Ignore if you already have the labeled image
        #-------------------------------------------------------------
        labeled_cyto_dir_path = os.path.join(raw_dir, 'Labeled_Images_Cytoplasm')
        print(f'{labeled_cyto_dir_path=}')
        if os.path.exists(labeled_cyto_dir_path):
            print('Using premade Labeled Image for Cytoplasm')
            labeled_cyto_path = os.path.join(segment_results_path, 'labeled_img_cyto.tif')
            already_labeled_image_cyto_path = os.path.join(labeled_cyto_dir_path, position)
            print(f'{already_labeled_image_cyto_path=}')
            copyfile(already_labeled_image_cyto_path, labeled_cyto_path)
        #-------------------------------------------------------------
        
        
        #-------------------------------------------------------------
        else:
            labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
            labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, cyto_channel = cyto_channel_num, num_wav = num_wav)
        #-------------------------------------------------------------
    #-------------------------------------------------------------

    else:
        
        
        #Ignore if you already have the labeled image for nuclei
        #-------------------------------------------------------------
        if 'Labeled_Images' in tiff_for_segment:
            labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
            copyfile(tiff_for_segment, labeled_img_path)
        #-------------------------------------------------------------
        
        # Get nuclei labeled image if true
        #-------------------------------------------------------------
        elif get_nuclei_img == True:
            labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
            label_img = get_labeled_img_cellpose(tiff_for_segment, num_wav, nuclei_channel_num, labeled_img_path,
                            nuclei_radius, flow_threshold, cell_prob_threshold, num_z = num_z)
        else:
            labeled_img_path = None
        #-------------------------------------------------------------
        
        
        #Ignore if you already have the labeled image for cytoplasm
        #-------------------------------------------------------------
        labeled_cyto_dir_path = os.path.join(raw_dir, 'Labeled_Images_Cytoplasm')
        print(f'{labeled_cyto_dir_path=}')
        if os.path.exists(labeled_cyto_dir_path):
            print('Using premade Labeled Image for Cytoplasm')
            labeled_cyto_path = os.path.join(segment_results_path, 'labeled_img_cyto.tif')
            already_labeled_image_cyto_path = os.path.join(labeled_cyto_dir_path, position)
            print(f'{already_labeled_image_cyto_path=}')
            copyfile(already_labeled_image_cyto_path, labeled_cyto_path)
        #-------------------------------------------------------------
        
        #Get Cytoplasm labeled image if true
        #-------------------------------------------------------------
        elif get_cyto_img == True:
            labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
            labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, 
                                cyto_channel = cyto_channel_num, num_wav = num_wav, 
                                cell_prob_threshold = cyto_cell_prob_threshold, 
                                cell_flow_threshold = cyto_flow_threshold,
                                cyto_radius = cyto_radius)
        else:
            labeled_cyto_path = None
        #-------------------------------------------------------------
        
        assert labeled_cyto_path != None or labeled_img_path != None 
        

    return labeled_img_path, labeled_cyto_path
    
def make_2d_into_3d(tiff_2d, num_z=20):
    
    #For edge case where num_z = 1
    #-------------------------------------------------------------
    if num_z == 1:
        num_z = 2
    #-------------------------------------------------------------
    
    #Stack the same z on top of each other
    #-------------------------------------------------------------
    tiff_3d = []
    for i in range(num_z):
        tiff_3d.append(tiff_2d)
        
    tiff_3d = np.array(tiff_3d).astype(np.int16)
    #-------------------------------------------------------------
    return tiff_3d
    
def save_tiff_3d_to_temp_file(tiff_3d, tiff_for_segment):
    
    #Make temp_dir and save
    #-------------------------------------------------------------
    temp_dir = os.path.join('/tmp', ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10)))
    temp_dir_labeled_img = os.path.join(temp_dir, 'Labeled_Images')
    os.makedirs(temp_dir_labeled_img)
    #-------------------------------------------------------------
    
    
    
    tiff_for_segment = os.path.join(temp_dir_labeled_img, os.path.basename(tiff_for_segment))
    #-------------------------------------------------------------    
    
    return tiff_for_segment
    
    
def get_tiff_for_segment(tiff_dir, position, num_z):
    
    #Get all directories
    #-------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    all_dirs = glob.glob(glob_me)
    #-------------------------------------------------------------
    
    #Check to see if segmentation is specified in a dir
    #-------------------------------------------------------------
    bools_seg_dir = [('segmentation' == a_dir.rsplit('/', 1)[-1]) for a_dir in all_dirs]
    bool_seg_dir = any(bools_seg_dir)
    
    bools_labeled_img_dir = [('Labeled_Images' == a_dir.rsplit('/', 1)[-1]) for a_dir in all_dirs]
    bool_labeled_img_dir = any(bools_labeled_img_dir)
    #-------------------------------------------------------------

    #If labeled image is already specified
    #-------------------------------------------------------------

    #if bool_labeled_img_dir:
    if bool_labeled_img_dir:    
        #Read in Labeled Image
        #-------------------------------------------------------------
        tiff_for_segment = os.path.join(tiff_dir, 'Labeled_Images', position)
        print(f'{tiff_for_segment=}')
        tiff = tf.imread(tiff_for_segment)
        print(f'{tiff.shape=}')
        #-------------------------------------------------------------
        
        #Check if 3d or 2d
        #-------------------------------------------------------------
        if len(tiff.shape) == 3:
            pass
        elif len(tiff.shape) ==2:
            
            print(f'{num_z=}')
            #Turn 2d into 3d
            #-------------------------------------------------------------
            tiff_3d = make_2d_into_3d(tiff, num_z)
            #-------------------------------------------------------------
            
            #Save tiff 3d to temp dir
            #-------------------------------------------------------------
            tiff_for_segment = save_tiff_3d_to_temp_file(tiff_3d, tiff_for_segment)
            #-------------------------------------------------------------
            
            print(f'{tiff_for_segment=}')
            tf.imwrite(tiff_for_segment, tiff_3d)
        else:
            raise Exception("The Labeled Image has to be 2d or 3d.")
    #-------------------------------------------------------------
    
    #If tiff to segment is already specified
    #-------------------------------------------------------------
    elif bool_seg_dir:
        tiff_for_segment = os.path.join(tiff_dir, 'segmentation', position)
        print(f'{tiff_for_segment=}')
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
    
def is_tiff_misformed(labeled_img_src):
    
    labeled_img = tf.imread(labeled_img_src)
    
    last_two_dims_equal = labeled_img.shape[1] != labeled_img.shape[2]
    
    return last_two_dims_equal
    
def save_labeled_img(tiff_dir, segment_results_path, position, edge_delete_dist, dist_between_nuclei, bool_cyto_match, \
        area_tol, cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, num_z, flow_threshold, 
        cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold, cyto_radius,
        debug = False):
            
    
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
        labeled_img_path, labeled_cyto_path = get_labeled_imgs(tiff_dir, position, segment_results_path, tiff_for_segment, bool_cyto_match, 
                                                cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, 
                                                num_z, flow_threshold, cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold,
                                                cyto_cell_prob_threshold, cyto_radius)
    #-------------------------------------------------------------
    
    
    # If you have a labeled image run post processing
    #-------------------------------------------------------------
    if labeled_img_path != None:
        label_img_post_processed_dst = os.path.join(segment_results_path, 'labeled_img_post.tif')
        post_process(edge_delete_dist, dist_between_nuclei, labeled_img_path, labeled_cyto_path, label_img_post_processed_dst)
        labeled_img_path = label_img_post_processed_dst
    #-------------------------------------------------------------
    
    #Check for Shape and path of labeled image
    #-------------------------------------------------------------
    print(f'{labeled_img_path=}')
    label_img = tf.imread(labeled_img_path)
    print(f'{label_img.shape=}')
    #-------------------------------------------------------------
    
    
    if is_tiff_misformed(labeled_img_path) and 'Labeled_Images' not in tiff_for_segment:
        print('Reshaping')
        print(f'{labeled_img_path=}')
        switch_low_z_to_right_shape(labeled_img_path)
        label_img = tf.imread(labeled_img_path)
        print(f'{label_img.shape=}')
        
        
    # Match the nuclei and cytoplasm
    #-------------------------------------------------------------
    if bool_cyto_match:
        print("Running Nuccy Match")
        nuclei_dst = os.path.join(segment_results_path, 'nuclei_labeled_img_matched.tif')
        cyto_dst = os.path.join(segment_results_path, 'cyto_labeled_img_matched.tif')
        get_matched_3d_img(labeled_img_path, labeled_cyto_path, area_tol, post_process_dir, segment_results_path, nuclei_dst, cyto_dst)
        
        return nuclei_dst
    
    #or dont match    
    else:
        
        #If there was no nuclei segmentation run return cytoplasm
        #-------------------------------------------------------------
        if labeled_img_path == None:
            return labeled_cyto_path
        else:
            return labeled_img_path
        #-------------------------------------------------------------
        
    #-------------------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_post_labeled_cyto':
        print('=---------------------------------------')
        tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1-big'
        segment_results_path = '/home/nrezaee/temp2'
        position  = 'MMStack_Pos0.ome.tif'
        edge = 0
        dist = 0
        bool_cyto_match = False
        area_tol = 1
        debug = False
        cyto_channel_num = 1
        get_nuc = True
        get_cyto = True
        num_z=2
        num_wav=4
        nuclei_radius = 0
        cell_prob_threshold= .5
        flow_threshold = .5
        nuclei_channel_num = -1
        cyto_flow_threshold = 0
        cyto_cell_prob_threshold = 0
        cyto_radius = 10
        save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol,
                    cyto_channel_num, get_nuc, get_cyto, num_wav, nuclei_radius, num_z, flow_threshold,
                    cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold,
                    cyto_radius = 10, debug=debug)

    if sys.argv[1] == 'debug_post_labeled_cyto_lex':
        print('=---------------------------------------')
        tiff_dir = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3'
        segment_results_path = '/home/nrezaee/temp2'
        position  = 'MMStack_Pos0.ome.tif'
        edge = 0
        dist = 0
        bool_cyto_match = False
        area_tol = 1
        debug = False
        cyto_channel_num = 1
        get_nuc = True
        get_cyto = True
        num_z=2
        num_wav=4
        nuclei_radius = 0
        cell_prob_threshold= .5
        flow_threshold = .5
        nuclei_channel_num = -1
        cyto_flow_threshold = 0
        cyto_cell_prob_threshold = 0
        cyto_radius = 10
        save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol,
                    cyto_channel_num, get_nuc, get_cyto, num_wav, nuclei_radius, num_z, flow_threshold,
                    cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold,
                    cyto_radius = 10, debug=debug)


    if sys.argv[1] == 'debug_post':
        print('=---------------------------------------')
        tiff_dir = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3/'
        segment_results_path = '/home/nrezaee/temp2'
        position  = 'MMStack_Pos1.ome.tif'
        edge = 8
        dist = 2
        bool_cyto_match = True
        area_tol = 1
        debug = False
        cyto_channel_num = 1
        get_nuc = True
        get_cyto = False
        num_z=1
        num_wav=2
        nuclei_radius = 0
        cell_prob_threshold= .5
        flow_threshold = .5
        nuclei_channel_num = -1
        cyto_flow_threshold = 0
        cyto_cell_prob_threshold = 0
        cyto_radius = 10
        save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol,
                    cyto_channel_num, get_nuc, get_cyto, num_wav, nuclei_radius, num_z, flow_threshold,
                    cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold,
                    cyto_radius = 10, debug=debug)

    if sys.argv[1] == 'debug_post_michal':
        print('=---------------------------------------')
        tiff_dir = '/groups/CaiLab/personal/Michal/raw/2021-06-21_Neuro4181_5_noGel_pool1/'
        segment_results_path = '/home/nrezaee/temp2'
        position  = 'MMStack_Pos1.ome.tif'
        edge = 8
        dist = 2
        bool_cyto_match = False
        area_tol = 1
        debug = False
        cyto_channel_num = 1
        get_nuc = True
        get_cyto = False
        num_z=1
        num_wav=2
        nuclei_radius = 0
        cell_prob_threshold= .5
        flow_threshold = .5
        nuclei_channel_num = -1
        cyto_flow_threshold = 0
        cyto_cell_prob_threshold = 0
        cyto_radius = 10
        save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol,
                    cyto_channel_num, get_nuc, get_cyto, num_wav, nuclei_radius, num_z, flow_threshold,
                    cell_prob_threshold, nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold,
                    cyto_radius = 10, debug=debug)
