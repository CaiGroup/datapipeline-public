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
import imageio as io
import imutils

def rotate_img(img_src, angle=-90):
    
    #Read and rotate image
    #---------------------------------------
    img = io.imread(img_src)
    rotated_img = imutils.rotate(img, angle=angle)
    
    #Check to see image
    #---------------------------------------
    plt.figure(figsize=(20,20))
    plt.imshow(rotated_img)
    #---------------------------------------
    
    #Save image
    #---------------------------------------
    io.imwrite(img_src, rotated_img)
    #---------------------------------------
    
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
    diff_bars = np.setdiff1d(df_barcode.iloc[:,0].apply(str), df_count_matrix.gene.apply(str))
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
    if 0 in cellIDs:
        cellIDs.remove(0)
    
    #-------------------------------------------------

    #Plot each cellID
    #-------------------------------------------------
    for cell in cellIDs:
        
        df_genes_cell = df_genes[df_genes.cellID == cell]
        plt.xlim((0, label_img.shape[1]))
        plt.ylim((0, label_img.shape[2]))
        plt.scatter(list(df_genes_cell.y), list(df_genes_cell.x), s = 1)
    #-------------------------------------------------
    
    #Save figure
    #-------------------------------------------------
    print('File Path of Genes on Cells:', dst)
    plt.savefig(dst)
    #-------------------------------------------------
    
    #Rotate saved image
    #-------------------------------------------------
    rotate_img(dst)
    #-------------------------------------------------
    
if sys.argv[1] == 'debug_plotted_assigned_genes':
    genes_csv = 'foo/cellpose_test_non_barcoded/gene_locations_assigned_to_cell.csv'
    dst = 'foo/assigned.png'
    labeled_img_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Segmentation/labeled_img_post.tif'
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
        df_gene_list['cellID'] = label_img[z, y, x]
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

def get_count_matrix(df_gene_list):
   
    #I found a one liner to get the count matrix lolololololololol
    #--------------------------------------------
    df_count_matrix = pd.crosstab(index=df_gene_list['gene'], columns=df_gene_list['cellID'])
    #--------------------------------------------
        
    #Clean up the indexes
    #--------------------------------------------
    df_count_matrix_reset_index = df_count_matrix.reset_index()
    df_count_matrix_reset_index.columns.name = None
    #--------------------------------------------
    
    #Add Cell to column names
    #--------------------------------------------
    column_list = list(df_count_matrix_reset_index.columns)
    cell_column_list = ['cell_' + str(cell_num) for cell_num in column_list if type(cell_num) != str]
    cell_column_list_with_gene = ['gene'] + cell_column_list

    df_count_matrix_reset_index.columns = cell_column_list_with_gene
    #--------------------------------------------
    
    return df_count_matrix_reset_index
    
def get_gene_cell_matrix(df_gene_list, labeled_img):
    """
    Inputs:
        df_gene_list - pandas dataframe (gene,x,y,z)
        labeled_img 
    Outputs:
        count_matrix
    """
    
    #Get count matrix
    # ---------------------------------------------------------------------
    df_gene_cell = get_count_matrix(df_gene_list)
    # ---------------------------------------------------------------------
    
    #Add Cells that do not have genes
    # ---------------------------------------------------------------------
    labels = np.unique(labeled_img)
    print(f'{len(labels)=}')
    df_gene_cell_all = add_empty_cells(df_gene_cell, labels)
    # ---------------------------------------------------------------------
    
    #Check if cell 0 is in cell columns
    # ---------------------------------------------------------------------
    if 'cell_0.0' in df_gene_cell_all.columns:
        df_gene_cell_all = df_gene_cell_all.drop(columns = ['cell_0.0']) 
    # ---------------------------------------------------------------------
    
    return df_gene_cell_all
    
if sys.argv[1] == 'debug_gene_cell_matrix':
    
    df_gene_list = pd.read_csv('/groups/CaiLab/analyses/real_arun/06212021_Automation_Testes_NoHydrogel/Testes_Strictness8/MMStack_Pos1/Segmentation/Channel_1/gene_locations_assigned_to_cell.csv')
    labeled_img_src = '/groups/CaiLab/analyses/real_arun/06212021_Automation_Testes_NoHydrogel/Testes_Strictness8/MMStack_Pos1/Segmentation/labeled_img_post.tif'
    labeled_img = tf.imread(labeled_img_src)
    df_gene_cell = get_gene_cell_matrix(df_gene_list, labeled_img)
    print(f'{df_gene_cell.shape=}')
    df_gene_cell.to_csv('foo/gene_cell.csv', index=False)

elif sys.argv[1] == 'debug_gene_cell_matrix_non_barcoded':
    
    df_gene_list = pd.read_csv('foo/cellpose_test_non_barcoded/gene_locations_assigned_to_cell.csv')
    barcode_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/BarcodeKey/sequential_key.csv'
    labeled_img_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Segmentation/labeled_img_post.tif'
    labeled_img = tf.imread(labeled_img_src)
    df_gene_cell = get_gene_cell_matrix(df_gene_list, labeled_img)
    print(f'{df_gene_cell.shape=}')
    df_gene_cell.to_csv('foo/gene_cell_non_barcoded.csv', index=False)

