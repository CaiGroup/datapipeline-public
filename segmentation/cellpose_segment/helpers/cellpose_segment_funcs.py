"""
Utilities to output dataframes for points using segmentation

"""
from numpy.core.multiarray import ndarray
from skimage.draw import polygon
from skimage.measure import regionprops_table

import numpy as np
import pandas as pd




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
    
    x = df_gene_list['x'].astype(int) - 1
    y = df_gene_list['y'].astype(int) - 1
    
    print(f'{label_img.shape=}')
    if 'z' in df_gene_list:
        z = df_gene_list['z'].astype(int) - 1
        print(f'{z=}')
        print(f'{y=}')
        print(f'{x=}')
        
        
        df_gene_list['cellID'] = label_img[z, x, y]
    else:
        df_gene_list['cellID'] = label_img[y, x]
    # ---------------------------------------------------------------------

    return df_gene_list

# #Test
# #--------------------------------------------------
# import tifffile
# decoded_genes_src = '/groups/CaiLab/analyses/nrezaee/2020-11-24-takei-2ch/takei_2ch_parallel/MMStack_Pos0/Decoded/Channel_1/pre_seg_diff_1_minseeds_2_unfiltered.csv'
# df_gene_list = pd.read_csv(decoded_genes_src)
# label_img_src = '/groups/CaiLab/analyses/nrezaee/2020-11-24-takei-2ch/takei_2ch_parallel/MMStack_Pos0/Segmentation/Channel_1/labeled_img.tiff'
# label_img = tifffile.imread(label_img_src)
# df_gene_list = assign_to_cells(df_gene_list, label_img)
# print(df_gene_list)

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


def get_gene_cell_matrix(df_gene_list):
    """
    Generate cell by gene matrices from the local df gene_list

    Parameters
    ----------
    df_gene_list : pandas data frame
        Columns: gene, x, y, z, intensity (optional), cellID

    Returns
    -------
    df_gene_cell : pandas data frame

    See also
    --------

    Notes
    -----
    """

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

    return df_gene_cell
