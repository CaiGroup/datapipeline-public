import os
import subprocess
import sys

def delete_edges(label_img_src, edge_delete_dist, post_process_dir):

    #Specify directory and files
    #-------------------------------------------------------------
    label_img_dir = os.path.dirname(label_img_src)
    nucboundzap_file_path = os.path.join(post_process_dir, 'edge_deletion', 'nucboundzap')    
    #-------------------------------------------------------------
    
    #Run the edge deleter
    #-------------------------------------------------------------
    print("Deleting Edges")
    out_names = subprocess.check_output(
        [nucboundzap_file_path, label_img_src, str(edge_delete_dist)]
    )
    out_names = out_names.decode().split('\n')
    #-------------------------------------------------------------
    
    #Return dst of labeled image
    #-------------------------------------------------------------
    print(f'{out_names=}')
    return out_names[0]
    #-------------------------------------------------------------

if __name__ == '__main__':

    if sys.argv[1] == 'debug_delete_edges':
        label_img_src = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_pos3_python_dot_strict_-2_rad_3/MMStack_Pos3/Segmentation/labeled_img_post.tif'
        edge_delete_dist = 2
        post_process_dir = '/home/nrezaee/test_cronjob_multi_dot/segmentation/post_processing'

        delete_edges(label_img_src, edge_delete_dist, post_process_dir)