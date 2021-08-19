import tifffile
import os
import tempfile
import pandas as pd
from scipy.io import loadmat
from .read_roi import read_roi_zip
import pandas as pd

from .helpers import roi_segment_funcs


def combine_barcodes(barcode_src1, barcode_src2):
    
    barcode1 = pd.read_csv(barcode_src1)
    barcode2 = pd.read_csv(barcode_src2)
    
    combined_barcodes = barcode1.append(barcode2).reset_index(drop=True)
    
    return combined_barcodes 


def get_df_from_mat(finalPosList, barcode, upto = None):
    
    df = pd.DataFrame(columns=['gene','x','y','z'])

    if upto == None or upto > len(finalPosList):
        num_genes = len(finalPosList)
    else:
        num_genes = upto

    for i in range(num_genes):
        gene_locs = finalPosList[i][0]
        gene_name = barcode['gene'][i]
        
        if num_genes >20:
            if i% (num_genes//20) == 0:
                print(f'{i=}')
        for gene_loc in gene_locs:
            
            if gene_loc.size != 0:
                x = gene_loc[0]
                y = gene_loc[1]
                z = gene_loc[2]
                df2 = pd.DataFrame([[gene_name, x, y, z]],columns=['gene','x','y','z'])
                df = df.append(df2)
            
    return df

def run_me(segmented_dir, decoded_genes_src, barcode_src, roi_zip_file_path, bool_fake_barcodes, num_zslices, channel_num = None):
    


    print(f'{decoded_genes_src=}')
    # finalPosList = loadmat(decoded_genes_src)['finalPosList']
    #-------------------------------------------
    
    print(f'{segmented_dir.split(os.sep)=}')
    
    

    print(f'{barcode_src=}')
    
    if bool_fake_barcodes == True:

        fake_barcode_src = os.path.join(os.path.dirname(barcode_src), 'fake_barcode.csv')      
        
        def combine_barcodes(barcode_src1, barcode_src2):
    
            barcode1 = pd.read_csv(barcode_src1)
            barcode2 = pd.read_csv(barcode_src2)
            
            combined_barcodes = barcode1.append(barcode2).reset_index(drop=True)
            
            return combined_barcodes 
    
        barcode = combine_barcodes(barcode_src, fake_barcode_src)
        
        
    else: 
        
        barcode = pd.read_csv(barcode_src)
    # #-------------------------------------------
    
    
    #Get df_gene_list
    #-------------------------------------------
    # generalPosList.shape=}')
    # print(f'{barcode.shape=}')
    # df_gene_list = get_df_from_mat(finalPosList, barcode)
    df_gene_list = pd.read_csv(decoded_genes_src).rename({'geneID': 'gene'}, axis='columns')
    
    #-------------------------------------------

    
    
    #Get 3d image
    #-------------------------------------------
    print("Reading ROI")
    roi = read_roi_zip(roi_zip_file_path)
    
    print("Getting Labeled Image")
    label_img = roi_segment_funcs.roi2mask(roi, num_zslices)
    
    print(f'{label_img.shape=}')
    
    
    if channel_num == None:
        segment_results_path = segmented_dir
        
    else:
        segment_results_path = os.path.join(segmented_dir, 'Channel_' + str(channel_num))
        if not os.path.exists(segment_results_path):
            os.makedirs(segment_results_path)
    
    labeled_img_path = os.path.join(segment_results_path, '3d_labeled_img.tiff')
    
    tifffile.imwrite(labeled_img_path, label_img)
    #-------------------------------------------
    
    
    #Assign genes to cells
    #-------------------------------------------
    df_gene_list_assigned_cell = roi_segment_funcs.assign_to_cells(df_gene_list, label_img)
    
    df_gene_list_assigned_cell_path = os.path.join(segment_results_path, 'gene_locations_assigned_to_cell.csv')
        
    df_gene_list_assigned_cell.to_csv(df_gene_list_assigned_cell_path,index=False)
    #-------------------------------------------
    
    
    #Get Cell Info
    #-------------------------------------------
    df_cell_info = roi_segment_funcs.get_cell_info(label_img)
    

    df_cell_info_path = os.path.join(segment_results_path, 'cell_info.csv')
        
    df_cell_info.to_csv(df_cell_info_path, index=False)
    #-------------------------------------------
    
    
    #Get Gene Matrix
    #-------------------------------------------
    df_gene_cell_matrix = roi_segment_funcs.get_gene_cell_matrix(df_gene_list_assigned_cell)
    df_gene_cell_matrix_path = os.path.join(segment_results_path, 'count_matrix.csv')
    df_gene_cell_matrix.to_csv(df_gene_cell_matrix_path,index=False)
    #-------------------------------------------
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
