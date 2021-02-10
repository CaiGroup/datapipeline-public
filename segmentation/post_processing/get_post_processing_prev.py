import subprocess
import os
from shutil import copyfile
import tifffile
import numpy as np
import sys

sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from segmentation.cellpose_segment.helpers import cellpose_segment_funcs
from segmentation.cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs


def post_process(edge_delete_dist, dist_between_nuclei, label_img_src, label_img_dst):
    
    label_img_dir = os.path.dirname(label_img_src)
    
    cwd = os.getcwd()
    post_process_dir = os.path.join(cwd, 'segmentation/post_processing')
    
    if dist_between_nuclei==0:
        pass
    else:
        print("Making Distance Between Cells")
        nuctouchresize_file_path = os.path.join(post_process_dir, 'nuctouchresize')
        subprocess.call(['sh', nuctouchresize_file_path, label_img_src, str(dist_between_nuclei)])
        label_img_src = os.path.join(label_img_dir, 'labeled_img_r' + str(dist_between_nuclei) + '.tif')
        print(f'{label_img_src=}')
        # tiff = tifffile.imread(label_img_src)
        # tifffile.imsave(label_img_src, tiff[:,:,:,0])
        
    if int(edge_delete_dist)  == 0:
        pass
    else:
        print("Deleting Edges")
        nucboundzap_file_path = os.path.join(post_process_dir, 'nucboundzap')
        subprocess.call(['sh', nucboundzap_file_path, label_img_src, str(edge_delete_dist)])
        label_img_src = os.path.join(label_img_dir, label_img_src.replace('.tif', '') + '_bzap_d' + str(edge_delete_dist) + '.tif')
        print(f'{label_img_src=}')
        
    print(f'{label_img_dst=}')
    copyfile(label_img_src, label_img_dst)
    

# dist = 5
# edge = 5
# src = '/home/nrezaee/sandbox/gmic_testing/pipeline/labeled_img.tif'
# dst= '/home/nrezaee/sandbox/gmic_testing/pipeline/labeled_img_result.tif'
# post_process(edge, dist, src, dst)

# tiff  = tifffile.imread(dst)
# print(f'{tiff.shape=}')
# print(f'{np.unique(tiff)=}')

        
    
def save_labeled_img(tiff_dir, segment_results_path, position, edge_delete_dist, dist_between_nuclei, debug = False):
    
    #print(f'{locals()=}')
    #Get Tiff for Segmentation
    #-----------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    sorted_hybs = get_and_sort_hybs(glob_me)
    assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"
      
    tiff_for_segment = os.path.join(sorted_hybs[0], position)
    #-----------------------------------------------------------------
    

    if debug == True:
        print('hi')
        
        #Get Labeled Image
        #------------------------------------------------------------------
        labeled_img_path = os.path.join('/home/nrezaee/sandbox/gmic_testing/data/', 'labeled_img.tif')
        
                
        label_img = tifffile.imread(labeled_img_path)
        labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
        
        
        #------------------------------------------------------------------
        
    else:
            
        #Get Labeled Image
        #------------------------------------------------------------------
        labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tif')
                
        label_img = get_labeled_img_cellpose(tiff_for_segment, labeled_img_path)
        #------------------------------------------------------------------
        
    if int(edge_delete_dist)  != 0 or dist_between_nuclei!=0:
        label_img_post_proccessed_dst = os.path.join(segment_results_path, 'labeled_img_post_processed.tif')
        post_process(edge_delete_dist, dist_between_nuclei, labeled_img_path, label_img_post_proccessed_dst)
    
        return label_img_post_proccessed_dst
    else:
        
        return labeled_img_path
    
# tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1'
# segment_results_path = '/groups/CaiLab/analyses/nrezaee/test1/3d_across/MMStack_Pos0/segmentation'
# position  = 'MMStack_Pos0.ome.tif'
# edge = 1
# dist = 1
# save_labeled_img(tiff_dir, segment_results_path, position, edge, dist, debug=False)

    
    
    
    
    
    
        