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

print(1)
sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from segmentation.cellpose_segment.helpers import cellpose_segment_funcs
from segmentation.cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs
from segmentation.post_processing.get_cyto_labeled_img import get_labeled_cyto_cellpose

from segmentation.post_processing.nuccymatch import get_matched_3d_img

def make_distance_between_cells(label_img_src, dist_between_nuclei, post_process_dir):
    
    label_img_dir = os.path.dirname(label_img_src)

    print("Making Distance Between Cells")
    nuctouchresize_file_path = os.path.join(post_process_dir, 'nuctouchresize')
    subprocess.call(['sh', nuctouchresize_file_path, label_img_src, str(dist_between_nuclei)])
    label_img_src = os.path.join(label_img_dir, 'labeled_img_r' + str(dist_between_nuclei) + '.tif')
    print(f'{label_img_src=}')
    
    return label_img_src
    
def delete_edges(label_img_src, edge_delete_dist, post_process_dir):

    label_img_dir = os.path.dirname(label_img_src)
    
    print("Deleting Edges")
    nucboundzap_file_path = os.path.join(post_process_dir, 'nucboundzap')
    subprocess.call(['sh', nucboundzap_file_path, label_img_src, str(edge_delete_dist)])
    label_img_src = os.path.join(label_img_dir, label_img_src.replace('.tif', '') + '_bzap_d' + str(edge_delete_dist) + '.tif')
    print(f'{label_img_src=}')
    
    return label_img_src

def get_debug():
    
    labeled_img_path ='/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_img_r12_bzap_d8.tif'
    
    labeled_cyto_path = '/groups/CaiLab/analyses/nrezaee/E14L22Rik/E14L22Rik_matched_1pos/MMStack_Pos0/Segmentation/labeled_cyto_img.tif'
    
    return labeled_img_path, labeled_cyto_path
    
def get_labeled_imgs(segment_results_path, tiff_for_segment, bool_cyto_match, cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav):
    
    
    if bool_cyto_match == True:
        labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
        label_img = get_labeled_img_cellpose(tiff_for_segment, dst = labeled_img_path, num_wav = num_wav)
        
        labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
        labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, cyto_channel = cyto_channel_num, num_wav = num_wav)
        
    else:
        
        if get_nuclei_img == True:
            labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
            label_img = get_labeled_img_cellpose(tiff_for_segment, dst = labeled_img_path, num_wav = num_wav)
        else:
            labeled_img_path = None
            
        if get_cyto_img == True:
            labeled_cyto_path = os.path.join(segment_results_path, 'labeled_cyto_img.tif')
            labeled_cyto = get_labeled_cyto_cellpose(tiff_for_segment, dst = labeled_cyto_path, cyto_channel = cyto_channel_num, num_wav = num_wav)
        else:
            labeled_cyto_path = None
        
    
        
        
    return labeled_img_path, labeled_cyto_path
    
def get_tiff_for_segment(tiff_dir, position):
    
    glob_me = os.path.join(tiff_dir, '*')
    all_dirs = glob.glob(glob_me)
    print(f'{all_dirs=}')
    bool_seg_dir = [('segmentation' == a_dir.rsplit('/', 1)[-1]) for a_dir in all_dirs]
    print(f'{bool_seg_dir=}')
    if any(bool_seg_dir):
        tiff_for_segment = glob.glob(os.path.join(tiff_dir, 'segmentation', position))[0]
        
    else:
        sorted_hybs = get_and_sort_hybs(glob_me)
        assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"
          
        tiff_for_segment = os.path.join(sorted_hybs[0], position)
        
    print(f'{tiff_for_segment=}')
       
    return tiff_for_segment
        
def post_process(edge_delete_dist, dist_between_nuclei, label_img_src, labeled_cyto_path, label_img_dst):
    
    
    
    cwd = os.getcwd()
    post_process_dir = os.path.join(cwd, 'segmentation/post_processing')
    
    if float(dist_between_nuclei)==0:
        pass
    else:
        label_img_src = make_distance_between_cells(label_img_src, int(float(dist_between_nuclei)), post_process_dir)
        
    if float(edge_delete_dist)  == 0:
        pass
    else:
        label_img_src = delete_edges(label_img_src, int(float(edge_delete_dist)), post_process_dir)
        
        
    print(f'{label_img_dst=}')
    copyfile(label_img_src, label_img_dst)
    
        
    
def save_labeled_img(tiff_dir, segment_results_path, position, edge_delete_dist, dist_between_nuclei, bool_cyto_match, \
        area_tol, cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav, debug = False):
    
    cwd = os.getcwd()
    post_process_dir = os.path.join(cwd, 'segmentation/post_processing')
    
    
    tiff_for_segment = get_tiff_for_segment(tiff_dir, position)
    
    print("Getting Labeled Images")
    if debug == True:
        labeled_img_path, labeled_cyto_path = get_debug()
        
    else:
        labeled_img_path, labeled_cyto_path = get_labeled_imgs(segment_results_path, tiff_for_segment, bool_cyto_match, \
                                                cyto_channel_num, get_nuclei_img, get_cyto_img, num_wav)
    
    if labeled_img_path != None:
        label_img_post_processed_dst = os.path.join(segment_results_path, 'labeled_img_post.tif')
        post_process(edge_delete_dist, dist_between_nuclei, labeled_img_path, labeled_cyto_path, label_img_post_processed_dst)
        labeled_img_path = label_img_post_processed_dst
        
    if bool_cyto_match:
        print("Running Nuccy Match")
        nuclei_dst = os.path.join(segment_results_path, 'nuclei_labeled_img_matched.tif')
        cyto_dst = os.path.join(segment_results_path, 'cyto_labeled_img_matched.tif')
        get_matched_3d_img(labeled_img_path, labeled_cyto_path, area_tol, post_process_dir, nuclei_dst, cyto_dst)
        
        return nuclei_dst
        
    else:
        
        if labeled_img_path == None:
            return labeled_cyto_path
        else:
            return labeled_img_path

    
if sys.argv[1] == 'debug_post':
    print('=---------------------------------------')
    tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/arun_1'
    segment_results_path = '/home/nrezaee/temp2'
    position  = 'MMStack_Pos0.ome.tif'
    edge = 0
    dist = 0
    bool_cyto_match = True
    area_tol = 1
    debug = False
    cyto_channel_num = 1
    get_nuc = True
    get_cyto = True
    save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, bool_cyto_match, area_tol, cyto_channel_num, get_nuc, get_cyto, num_wav = 4, debug=debug)

    
    
    
    
    
    
        