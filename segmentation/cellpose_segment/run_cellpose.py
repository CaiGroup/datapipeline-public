import tifffile
import os
import tempfile
import pandas as pd
from scipy.io import loadmat
import pandas as pd
import sys



sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from segmentation.cellpose_segment.helpers import cellpose_segment_funcs
from segmentation.cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs

def run_me(tiff_dir, segment_results_path, decoded_genes_src, position, bool_fake_barcodes, channel_num = None):
    
    
    print(f'{locals()=}')
    #Get Tiff for Segmentation
    #-----------------------------------------------------------------
    glob_me = os.path.join(tiff_dir, '*')
    sorted_hybs = get_and_sort_hybs(glob_me)
    
    assert len(sorted_hybs) >=1, "There were no Directories found in the hyb dir"
      
    tiff_for_segment = os.path.join(sorted_hybs[0], position)
    #-----------------------------------------------------------------
  
    
    #Get Labeled Image
    #------------------------------------------------------------------
    labeled_img_path = os.path.join(segment_results_path, 'labeled_img.tiff')
            
    label_img = get_labeled_img_cellpose(tiff_for_segment, labeled_img_path)
    #------------------------------------------------------------------
    
    #Get Gene List
    #------------------------------------------------------------------
    df_gene_list = pd.read_csv(decoded_genes_src).rename({'geneID': 'gene'}, axis='columns')
    #------------------------------------------------------------------
    
    #Assign genes to cells
    #-------------------------------------------
    print(f'{label_img.shape=}')
    df_gene_list_assigned_cell = cellpose_segment_funcs.assign_to_cells(df_gene_list, label_img)
    
    df_gene_list_assigned_cell_path = os.path.join(segment_results_path, 'gene_locations_assigned_to_cell.csv')
    
    print(f'{df_gene_list_assigned_cell_path=}')    
    df_gene_list_assigned_cell.to_csv(df_gene_list_assigned_cell_path)
    #-------------------------------------------
    
    
    #Get Cell Info
    #-------------------------------------------
    df_cell_info = cellpose_segment_funcs.get_cell_info(label_img)
    

    df_cell_info_path = os.path.join(segment_results_path, 'cell_info.csv')
    print(f'{df_cell_info_path=}')    
    df_cell_info.to_csv(df_cell_info_path)
    #-------------------------------------------
    
    
    #Get Gene Matrix
    #-------------------------------------------
    df_gene_cell_matrix = cellpose_segment_funcs.get_gene_cell_matrix(df_gene_list_assigned_cell)
    df_gene_cell_matrix_path = os.path.join(segment_results_path, 'count_matrix.csv')
    print(f'{df_gene_cell_matrix_path=}')
    df_gene_cell_matrix.to_csv(df_gene_cell_matrix_path)
    #-------------------------------------------
    

    
    
    


# #Test
# #-------------------------------------------------------------------
# tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/2020-11-24-takei-2ch'
# segmented_dst_dir = '/groups/CaiLab/analyses/nrezaee/2020-11-24-takei-2ch/takei_2ch_parallel/MMStack_Pos0/Segmentation'
# decoded_genes_src = '/groups/CaiLab/analyses/nrezaee/2020-11-24-takei-2ch/takei_2ch_parallel/MMStack_Pos0/Decoded/Channel_1/pre_seg_diff_1_minseeds_2_unfiltered.csv'
# position = 'MMStack_Pos0.ome.tif'
# bool_fake_barcodes = True
# channel=None

# run_me(tiff_dir, segmented_dst_dir, decoded_genes_src, position, bool_fake_barcodes, channel_num = channel)















