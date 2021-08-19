import os
import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def get_correlation_plot(decoded_csv_1, decoded_csv_2, sub_axes):
    """
    Get Correlation plots of two positions
    """
    
    df_1 = pd.read_csv(decoded_csv_1)
    df_2 = pd.read_csv(decoded_csv_2)
    
    dict_1 = df_1.gene.value_counts().to_dict()
    dict_2 = df_2.gene.value_counts().to_dict()
    
    dict_intersect_1 = {x:dict_1[x] for x in dict_1 
                                  if x in dict_2}
    dict_intersect_2 = {x:dict_2[x] for x in dict_2 
                                  if x in dict_1}
        
    assert set(dict_intersect_1) == set(dict_intersect_2) 
    
    list_count_1 = []
    list_count_2 = []
    for key in dict_intersect_2:
        list_count_1.append(dict_intersect_1[key])
        list_count_2.append(dict_intersect_2[key])
        
    #sub_axes.figure(figsize=(20,20))
    sub_axes.scatter(list_count_1, list_count_2)
    print(f'{pearsonr(list_count_1, list_count_2)=}')

def get_correlated_positions(analysis_dir):
    """
    Correlate all positions in one analysis dir
    """
    
    #Get Position Dirs
    #----------------------------------------------------------
    position_dirs_glob = os.path.join(analysis_dir, 'MMStack_Pos*')
    position_dirs = glob.glob(position_dirs_glob)
    print(f'{position_dirs=}')
    #----------------------------------------------------------
    
    #Get Channel Dirs
    #----------------------------------------------------------
    first_position_dir = position_dirs[0]
    channel_dirs = os.listdir(os.path.join(first_position_dir, 'Segmentation'))
    channel_dirs = [channel_dir for channel_dir in channel_dirs if 'Channel' in channel_dir]
    print(f'{channel_dirs=}')
    #----------------------------------------------------------
    
    #For Channel in analysis get Correlation plot
    #----------------------------------------------------------
    for channel_dir in channel_dirs:
        figure, axes = plt.subplots(nrows=len(position_dirs), ncols=len(position_dirs), figsize=(20,20))
        #For Each positions compare with each position
        for pos_index_1 in range(len(position_dirs)):
            decoded_genes_csv_1 = os.path.join(position_dirs[pos_index_1], 'Segmentation', channel_dir, 'gene_locations_assigned_to_cell.csv')
            for pos_index_2 in range(len(position_dirs)):
                decoded_genes_csv_2 = os.path.join(position_dirs[pos_index_2], 'Segmentation', channel_dir, 'gene_locations_assigned_to_cell.csv')
                print('--------------------------------------------------')

                get_correlation_plot(decoded_genes_csv_1, decoded_genes_csv_2, axes[pos_index_1, pos_index_2])
                
        channel_num = int('Channel_1'.split('Channel_')[1])
        
        #Set Column Names
        #----------------------------------------------------------
        cols = list(range(len(position_dirs)))
        col_labels = ['Position_' + str(col) for col in cols]
        for ax, col in zip(axes[0], col_labels):
            ax.set_title(col)
        #----------------------------------------------------------
        
        #Set Row Names
        #----------------------------------------------------------
        rows = list(range(len(position_dirs)))
        row_labels = ['Position_' + str(row) for row in rows]
        for ax, row in zip(axes[:,0], row_labels):
            ax.set_ylabel(row, rotation=0, size='large')
        #----------------------------------------------------------
        
        figure.savefig('correlation_channel_' + str(channel_num) + '.png')


if __name__ == '__main__':

    if sys.argv[1] == 'debug_corr_positions':
        analysis_dir = '/groups/CaiLab/analyses/michalp/michal_2/michal_2_decoding_test_ch2/'
        get_correlated_positions(analysis_dir)
    
        
        
    