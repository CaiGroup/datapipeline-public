"""
Utilities to output dataframes for points using segmentation

"""
from numpy.core.multiarray import ndarray
from skimage.draw import polygon
from skimage.measure import regionprops_table

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tifffile as tf
import sys
import os

def include_genes_not_in_count_matrix(count_src, barcode_src):
    """
    Get Genes not included in count matrix and add rows of zeros with it
    """
    
    #Load Dataframes
    #-------------------------------------
    df_count_matrix = pd.read_csv(count_src)
    df_barcode = pd.read_csv(barcode_src)
    #-------------------------------------
    
    #Check for off barcodes
    #-------------------------------------
    off_barcode_file_name = os.path.basename(barcode_src).split('.csv')[0] + '_fake.csv'
    off_barcode_src = os.path.join(os.path.dirname(barcode_src), off_barcode_file_name)
    print(f'{off_barcode_src=}')
    if os.path.isfile(off_barcode_src):
        df_off_barcode = pd.read_csv(off_barcode_src)
        df_barcode = df_barcode.append(df_off_barcode)
    #-------------------------------------
    
    #Get Genes not included
    #-------------------------------------
    diff_bars = np.setdiff1d(df_barcode.iloc[:,0], df_count_matrix.gene)
    #-------------------------------------
    
    #Include Genes not in Count matrix
    #-------------------------------------
    for diff_bar in diff_bars:
        
        #Make new row to include
        #-------------------------------------
        new_row_dict = {}    
        cols = list(df_count_matrix.columns)
        cols.remove('gene')
        new_row_dict['gene'] = diff_bar
        #-------------------------------------
        
        print(f'{diff_bar=}')
        #Make other columns zero
        #-------------------------------------
        for col in cols:
            new_row_dict[col] = 0
        #-------------------------------------
        
        #Add row
        #-------------------------------------
        df_count_matrix = df_count_matrix.append(new_row_dict, ignore_index=True)
        print(f'{df_count_matrix.shape=}')
        #-------------------------------------
        
    #Save new count matrix
    #-------------------------------------
    df_count_matrix.to_csv(count_src, index = False)
    #-------------------------------------
    

def get_plotted_assigned_genes(assigned_genes_csv_src, dst, label_img):
    
    #Plot labeled image
    #-------------------------------------------------
    plt.figure(figsize=(20,20))
    print(f'{label_img.shape=}')
    label_img = np.swapaxes(label_img, 1, 2)
    plt.imshow(label_img[label_img.shape[0]//2,:,:])
    #-------------------------------------------------
    
    #Load Genes and get CellIDs
    #-------------------------------------------------
    df_genes = pd.read_csv(assigned_genes_csv_src)
    cellIDs = list(df_genes.cellID.unique())
    #cellIDs.remove(0)
    
    #-------------------------------------------------

    #Plot each cellID
    #-------------------------------------------------
    for cell in cellIDs:
        df_genes_cell = df_genes[df_genes.cellID == cell]
        plt.xlim((0,2048))
        plt.ylim((0,2048))
        plt.scatter(list(df_genes_cell.x), list(df_genes_cell.y), s = 1)
    #-------------------------------------------------
    
    #Save figure
    #-------------------------------------------------
    print('File Path of Genes on Cells:', dst)
    plt.savefig(dst)
    #-------------------------------------------------
    
if sys.argv[1] == 'debug_plotted_assigned_genes':
    genes_csv = '/groups/CaiLab/analyses/alinares/2021_0512_mouse_hydrogel/anthony_test_1/MMStack_Pos6/Segmentation/Channel_1/gene_locations_assigned_to_cell.csv'
    dst = 'foo/assigned.png'
    labeled_img_src = '/groups/CaiLab/analyses/alinares/2021_0512_mouse_hydrogel/anthony_test_1/MMStack_Pos6/Segmentation/labeled_img_post.tif'
    labeled_img = tf.imread(labeled_img_src)
    get_plotted_assigned_genes(genes_csv, dst, labeled_img)

def assign_to_cells(df_gene_list, label_img):
    """
    Assigns points in df to a cell id using the labeled image

    Parameters
    ----------
    df_gene_list : data frame
        Columns: gene, x, y, z, intensity (optional)

    label_img : ndarray
        Label image for each cell (cellID > 0), where 0 is the background

    Returns
    -------
    df_gene_list : data frame adds 'cellID' column

    See also
    --------

    Notes
    -----
    - Testing for 2D images required
    """
    print(f'{label_img.shape=}')
    # convert polygon vertices to labeled image for each cell
    # ---------------------------------------------------------------------
    
    label_img = np.append(label_img, np.zeros((20, label_img.shape[1], label_img.shape[2])), axis=0)
    
   # df_gene_list = df_gene_list[df_gene_list['z'] < label_img.shape[0]]
    
    df_gene_list = df_gene_list[(df_gene_list.x < label_img.shape[1]) & (df_gene_list.x >= 0)]
    df_gene_list = df_gene_list[(df_gene_list.y < label_img.shape[2]) & (df_gene_list.y >= 0)]
    df_gene_list = df_gene_list[(df_gene_list.z < label_img.shape[0]) & (df_gene_list.z >= 0)]
        
    x = df_gene_list['x'].astype(int) 
    y = df_gene_list['y'].astype(int) 
    print(f'{label_img.shape=}')

    if 'z' in df_gene_list:
        
        z = df_gene_list['z'].astype(int) 
        print(z.head())
        print(x.head())
        print(y.head())
        df_gene_list['cellID'] = label_img[z, x, y]
    else:
        df_gene_list['cellID'] = label_img[x, y]
    # ---------------------------------------------------------------------

    return df_gene_list

if sys.argv[1] == 'debug_assign_to_cells':
    import tifffile
    decoded_genes_src = '/groups/CaiLab/analyses/nrezaee/test1-big/non_barcoded/MMStack_Pos0/Decoded/sequential_decoding_results.csv'
    df_gene_list = pd.read_csv(decoded_genes_src)
    label_img_src = '/groups/CaiLab/analyses/nrezaee/test1-big/non_barcoded/MMStack_Pos0/Segmentation/labeled_img.tif'
    label_img = tifffile.imread(label_img_src)
    print(f'{label_img.shape=}')
    df_gene_list = assign_to_cells(df_gene_list, label_img)
    print(df_gene_list)
    

def get_cell_info(label_img):
    """
    Returns the cell information from the labeled image as a df

    Parameters
    ----------
    label_img : ndarray
        Label image for each cell (cellID > 0), where 0 is the background

    Returns
    -------
    df_cell_info : pandas data frame

    See also
    --------

    Notes
    -----
    - scikit-image==1.16.1
    - numpy==1.16.0
    - Testing for 2D images required
    """

    # use scikit-image to return labels for cells, area, and centroids
    # ---------------------------------------------------------------------
    props = regionprops_table(label_img, properties=['label', 'area', 'centroid'])
    df_cell_info = pd.DataFrame(props)
    if 'centroid-2' in df_cell_info:
        df_cell_info = df_cell_info.rename(
            columns={"label": "cellID", "centroid-0": "y", "centroid-1": "x", "centroid-2": "z"})
    else:
        df_cell_info = df_cell_info.rename(
            columns={"label": "cellID", "centroid-0": "y", "centroid-1": "x"})
    # ---------------------------------------------------------------------

    return df_cell_info


def add_empty_cells(df_gene_cell, labels):
    """
    Adds cells that did not have any genes
    """
    
    #Make the variable that will have all genes
    #------------------------------------------------------
    df_gene_cell_all = df_gene_cell
    #------------------------------------------------------
    
    #Make all the columns
    #------------------------------------------------------
    for i in labels:
        gene_column = 'cell_'+str(i) + '.0'

        if gene_column not in df_gene_cell.columns:
            df_gene_cell_all[gene_column] = 0
    #------------------------------------------------------
    

    #Get Cell indices
    #------------------------------------------------------
    cell_cols = list(df_gene_cell_all.columns)[1:]
    cell_indices = []
    for i in range(len(cell_cols)):
        index = float(cell_cols[i].split('cell_')[1])
        cell_indices.append(index)
    #------------------------------------------------------
        
    #Sort the cell indices
    #------------------------------------------------------
    sorted_indices = sorted(cell_indices)
    sorted_cols = []
    for index in sorted_indices:
        sorted_cols.append('cell_'+str(index))
    #------------------------------------------------------
        
    #Move the columns to be sorted cell indices
    #------------------------------------------------------
    sorted_cols.insert(0, 'gene')
    df_gene_cell_all_sorted = df_gene_cell_all[sorted_cols]
    #------------------------------------------------------
    
    return df_gene_cell_all_sorted

def get_gene_cell_matrix(df_gene_list, labeled_img):

    # keep all cells > 0
    # ---------------------------------------------------------------------
    keep = df_gene_list['cellID'] > 0
    df_keep = df_gene_list[keep]
    # ---------------------------------------------------------------------

    # unique gene dict and add to df
    # ---------------------------------------------------------------------
    dict_keep = {"gene": df_keep.gene.unique()}
    df_gene_cell = pd.DataFrame.from_dict(dict_keep)
    # ---------------------------------------------------------------------

    # get and sort all unique cellIDs
    # ---------------------------------------------------------------------
    u_cell = df_keep.cellID.unique()
    u_cell = np.sort(u_cell)
    # ---------------------------------------------------------------------

    # Convert to list
    u_cell_list = u_cell.tolist()
    # Dictionary with index as value for correct column
    #  note: cells with 0 counts in all genes are excluded -> need to reindex
    cell_index = {val: idx + 1 for idx, val in enumerate(u_cell_list)}
    # ---------------------------------------------------------------------

    # print columns for each unique cell, set = 0
    # ---------------------------------------------------------------------
    for cell in u_cell:
        str_cell = 'cell_' + cell.astype(str)
        df_gene_cell[str_cell] = 0
    # ---------------------------------------------------------------------

    # loop through each gene, retrieve counts for each cellID
    # ---------------------------------------------------------------------
    num_rows = df_gene_cell.shape[0]
    for i in range(num_rows):
        # get each gene ID
        gene_name = df_gene_cell["gene"].iloc[i]

        # get all cells from df_keep
        df_section = df_keep[df_keep["gene"] == gene_name]

        # group by cell
        df_cell = df_section.groupby("cellID")

        # for each cell_id, add the number of points in the group
        for cell_id, group in df_cell:
            df_gene_cell.iloc[i, cell_index[cell_id]] += group.shape[0]
    # ---------------------------------------------------------------------
    labels = np.unique(labeled_img)
    df_gene_cell_all = add_empty_cells(df_gene_cell, labels)
    
    if 'cell_0.0' in df_gene_cell_all.columns:
        df_gene_cell_all = df_gene_cell_all.drop(columns = ['cell_0.0']) 
    
    return df_gene_cell_all
    
if sys.argv[1] == 'debug_gene_cell_matrix':
    
    df_gene_list = pd.read_csv('/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Segmentation/Channel_1/gene_locations_assigned_to_cell.csv')
    barcode_src = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/barcode_key/channel_1.csv'
    labeled_img_src = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Segmentation/labeled_img_post.tif'
    labeled_img = tf.imread(labeled_img_src)
    df_gene_cell = get_gene_cell_matrix(df_gene_list, labeled_img)
    print(f'{df_gene_cell.shape=}')
    df_gene_cell.to_csv('foo/gene_cell.csv', index=False)

