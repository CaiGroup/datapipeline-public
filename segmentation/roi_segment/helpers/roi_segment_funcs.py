"""
Utilities to output dataframes for points using segmentation

"""
from numpy.core.multiarray import ndarray
from skimage.draw import polygon
from skimage.measure import regionprops_table

import numpy as np
import pandas as pd


def roi2mask(roi: dict, num_z=1):
    """
    Returns an RoiSet.zip into a labeled mask

    Parameters
    ----------
    roi : dict
        Dictionary of x, y vertices

    num_z : int, optional
        Number of z-slices in the image. Defaults to 1

    Returns
    -------
    label_img : ndarray

    See also
    --------
    read_roi : reads in RoiSet.zip and creates roi : dict

    Notes
    -----
    Projects all 2D polygons to all z-slices.
    """

    # convert polygon vertices to labeled image for each cell
    # ---------------------------------------------------------------------
    label_img = np.zeros((2048, 2048, num_z), dtype=np.uint8)
    cell_id = 1

    # Create polygon from vertices
    # ---------------------------------------------------------------------
    for key in roi:
        # get x, y indices of polygon
        r = roi[key]['y']
        c = roi[key]['x']

        # make polygon
        rr, cc = polygon(r, c)
        label_img[rr, cc, :] = cell_id
        cell_id += 1
    # ---------------------------------------------------------------------

    return label_img


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
    x = df_gene_list['x'].astype(int) - 1
    y = df_gene_list['y'].astype(int) - 1
    if 'z' in df_gene_list:
        z = df_gene_list['z'].astype(int) - 1
        df_gene_list['cellID'] = label_img[y, x, z]
    else:
        df_gene_list['cellID'] = label_img[y, x]
    # ---------------------------------------------------------------------

    return df_gene_list


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
