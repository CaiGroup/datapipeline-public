"""
Utilities to output dataframes for points using segmentation

"""
from numpy.core.multiarray import ndarray
from skimage.draw import polygon
from skimage.measure import regionprops_table

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

def get_plotted_assigned_genes(assigned_genes_csv_src, dst, label_img):
    plt.figure(figsize=(20,20))
    plt.imshow(label_img[:,:,label_img.shape[2]//2])
    df_genes = pd.read_csv(assigned_genes_csv_src)
    cellIDs = df_genes.cellID.unique()

    for cell in cellIDs:
        print(cell)
        df_genes_cell = df_genes[df_genes.cellID == cell]
        plt.xlim((0,2048))
        plt.ylim((0,2048))
        plt.scatter(list(df_genes_cell.x), list(df_genes_cell.y), s = 1)
    
    plt.savefig(dst)

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
    df_gene_cell_all = df_gene_cell

    for i in labels:
        gene_column = 'cell_'+str(i) + '.0'

        if gene_column not in df_gene_cell.columns:
            df_gene_cell_all[gene_column] = 0
    
    bool_cols = []
    for col in df_gene_cell.columns:
        bool_cols.append(df_gene_cell[col] == df_gene_cell_all[col])
    
    cell_cols = list(df_gene_cell_all.columns)[1:]
    cell_indices = []
    for i in range(len(cell_cols)):
        index = float(cell_cols[i].split('cell_')[1])
        cell_indices.append(index)
        
    sorted_indices = sorted(cell_indices)
    sorted_cols = []
    for index in sorted_indices:
        sorted_cols.append('cell_'+str(index))
        
    sorted_cols.insert(0, 'gene')
    df_gene_cell_all_sorted = df_gene_cell_all[sorted_cols]
    
    return df_gene_cell_all_sorted

def get_gene_cell_matrix(df_gene_list, labeled_img):

    # Organize code by gene and count unique cellIDs
    # ---------------------------------------------------------------------
    # keep all cells > 0
    keep = df_gene_list['cellID'] > 0
    df_keep = df_gene_list[keep]

    # unique gene dict and add to df
    dict_keep = {"gene": df_keep.gene.unique()}
    df_gene_cell = pd.DataFrame.from_dict(dict_keep)

    # get and sort all unique cellIDs
    u_cell = df_keep.cellID.unique()
    u_cell = np.sort(u_cell)

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
    
    return df_gene_cell_all

