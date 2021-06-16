import tifffile
import os
import tempfile
import pandas as pd
from scipy.io import loadmat
import pandas as pd
import sys



sys.path.insert(0, os.getcwd())
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose
from segmentation.cellpose_segment.helpers import cellpose_segment_funcs
from segmentation.cellpose_segment.helpers.reorder_hybs import get_and_sort_hybs

def run_me(tiff_dir, segment_results_path, decoded_genes_src, barcode_key_src, position, label_img):
    
    
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
    df_gene_list_assigned_cell.to_csv(df_gene_list_assigned_cell_path, index=False)
    #-------------------------------------------
    
    
    #Get Cell Info
    #-------------------------------------------
    df_cell_info = cellpose_segment_funcs.get_cell_info(label_img)
    

    df_cell_info_path = os.path.join(segment_results_path, 'cell_info.csv')
    print(f'{df_cell_info_path=}')    
    df_cell_info.to_csv(df_cell_info_path)
    #-------------------------------------------
    
    
    #Get Gene Cell Matrix (Count Matrix)
    #-------------------------------------------
    df_gene_cell_matrix = cellpose_segment_funcs.get_gene_cell_matrix(df_gene_list_assigned_cell, label_img)
    df_gene_cell_matrix_path = os.path.join(segment_results_path, 'count_matrix.csv')
    print(f'{df_gene_cell_matrix_path=}')
    df_gene_cell_matrix.to_csv(df_gene_cell_matrix_path, index = False)
    cellpose_segment_funcs.include_genes_not_in_count_matrix(df_gene_cell_matrix_path, barcode_key_src)
    #-------------------------------------------
    
    
    #Plot Genes Assigned to Cell
    #-------------------------------------------
    plot_dst = os.path.join(segment_results_path, 'Genes_Assigned_to_Cells_Plotted.png')
    
    cellpose_segment_funcs.get_plotted_assigned_genes(df_gene_list_assigned_cell_path, plot_dst, label_img)
    #-------------------------------------------


if sys.argv[1] == 'debug_run_cellpose':
    
    tiff_dir = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/'
    segmented_dst_dir = '/home/nrezaee/test_cronjob_multi_dot/foo/cellpose_test'
    os.makedirs(segmented_dst_dir, exist_ok=True)
    decoded_genes_src = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Segmentation/Channel_1/gene_locations_assigned_to_cell.csv'
    position = 'MMStack_Pos0.ome.tif'
    barcode_key_src = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/barcode_key/channel_1.csv'
    
    labeled_img_src = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Segmentation/labeled_img_post.tif'
    labeled_img = tifffile.imread(labeled_img_src)
    
    run_me(tiff_dir, segmented_dst_dir, decoded_genes_src, barcode_key_src, position, labeled_img)
    
if sys.argv[1] == 'debug_run_cellpose_non_barcoded':
    
    tiff_dir = '/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013'
    segmented_dst_dir = '/home/nrezaee/test_cronjob_multi_dot/foo/cellpose_test_non_barcoded'
    os.makedirs(segmented_dst_dir, exist_ok=True)
    decoded_genes_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Decoded/sequential_decoding_results.csv'
    position = 'MMStack_Pos1.ome.tif'
    barcode_key_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/BarcodeKey/sequential_key.csv'
    
    labeled_img_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Segmentation/labeled_img_post.tif'
    labeled_img = tifffile.imread(labeled_img_src)
    
    run_me(tiff_dir, segmented_dst_dir, decoded_genes_src, barcode_key_src, position, labeled_img)
    














