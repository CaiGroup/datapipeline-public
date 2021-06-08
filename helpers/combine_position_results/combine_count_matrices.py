import os
import sys
import glob
import pandas as pd
import numpy as np

def combine_two_count_matrices(df1, count_matrix_src):
    """
    Combine two count matrices
    """
    
    df2 = pd.read_csv(count_matrix_src)
    
    print(f'{df1.shape=}')
    print(f'{df2.shape=}')
        
    print(f'{df1.gene=}')
    df1.gene.unique()
    df2.gene.unique()
    
    #Get Differences in Count Matrices
    #-------------------------------------------------
    not_in_df2 = np.setdiff1d(df1.gene.unique(), df2.gene.unique() )
    not_in_df1 = np.setdiff1d(df2.gene.unique(), df1.gene.unique())
    #-------------------------------------------------
    
    #Put Missing Genes in df2
    #-------------------------------------------------
    for missing_gene in not_in_df2:
        row_to_add = [missing_gene] + list(np.full( (df2.shape[1]-1), 0)) 
        df2.loc[len(df2)] = row_to_add
    #-------------------------------------------------
    
    #Put Missing Genes in df1
    #-------------------------------------------------
    for missing_gene in not_in_df1:
        row_to_add = [missing_gene] + list(np.full( (df1.shape[1]-1), 0)) 
        df1.loc[len(df1)] = row_to_add
    #-------------------------------------------------
    
    #Make sure rows equal each other 
    #-------------------------------------------------
    assert set(df1.gene.unique()) == set(df2.gene.unique()), 'The two count matrices have different genes.'
    #-------------------------------------------------
    
    #Add horizontally
    #-------------------------------------------------
    combined_df = pd.concat([df1, df2.drop(columns=['gene'], axis = 1)], axis=1)
    #-------------------------------------------------
    
    return combined_df



def get_combined_count_matrix(analysis_dir, dst):
    """
    Combine all count matrices for all
    """
    
    assert os.path.exists(analysis_dir), 'The analysis directory does not exist.'
    
    #Get All Dirs with count Matrices
    #----------------------------------------
    glob_me_for_channels = os.path.join(analysis_dir, 'MMStack_Pos*', 'Segmentation','Channel_*')
    print(f'{glob_me_for_channels=}')
    all_seg_dirs = glob.glob(glob_me_for_channels)
    
    if len(all_seg_dirs) == 0:
        all_seg_dirs = glob.glob(os.path.join(analysis_dir, 'MMStack_Pos*', 'Segmentation','*'))
    #----------------------------------------
    
    
    #Get All count_matrices
    #----------------------------------------
    assert len(all_seg_dirs) > 0, "There were no count matrices found."
    all_count_matrices = [os.path.join(seg_dir, 'count_matrix.csv') for seg_dir in all_seg_dirs]
    
    for count_matrix in all_count_matrices:
        assert os.path.isfile(count_matrix), 'One of the count matrices is missing.'
    #----------------------------------------
    
    
    #Comebine all count matrices
    #----------------------------------------
    comb_count_matrices = pd.read_csv(all_count_matrices[0])
    
    for i in range(1, len(all_count_matrices)):
        print(f'{all_count_matrices[i]=}')
        comb_count_matrices = combine_two_count_matrices(comb_count_matrices, all_count_matrices[i])
        print(f'{i=}')
        print(f'{comb_count_matrices.shape=}')
    #----------------------------------------
    
    #Save all combined count matrices
    #----------------------------------------
    comb_count_matrices.to_csv(dst, index=False)
    #----------------------------------------

if sys.argv[1] == 'debug_comb_count_matrices':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4/jina_pseudos_4_all_pos_all_chs/'
    dst = 'foo.csv'
    get_combined_count_matrix(analysis_dir, dst)




