import os
import subprocess
import sys

def make_distance_between_cells(label_img_src, dist_between_nuclei, post_process_dir):
    
    #Specify directory and files
    #-------------------------------------------------------------
    label_img_dir = os.path.dirname(label_img_src)
    nuctouchresize_file_path = os.path.join(post_process_dir, 'distance_between_cells', 'nuctouchresize')
    #-------------------------------------------------------------
    
    #Run the distance maker
    #-------------------------------------------------------------
    print("Making Distance Between Cells")
    print(f'{label_img_src=}')
    subprocess.call(['sh', nuctouchresize_file_path, label_img_src, str(dist_between_nuclei)])
    #-------------------------------------------------------------
    
    #Return Labeled image location
    #-------------------------------------------------------------
    label_img_src = os.path.join(label_img_dir, 'labeled_img_r' + str(dist_between_nuclei) + '.tif')
    print(f'{label_img_src=}')
    return label_img_src
    #-------------------------------------------------------------
    
if sys.argv[1] == 'debug_distance_between_cells':
    label_img_src = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_pos3_python_dot_strict_-2_rad_3/MMStack_Pos3/Segmentation/labeled_img.tif'
    distance_between_cells = 2
    post_process_dir = '/home/nrezaee/test_cronjob_multi_dot/segmentation/post_processing'
    
    make_distance_between_cells(label_img_src, distance_between_cells, post_process_dir)