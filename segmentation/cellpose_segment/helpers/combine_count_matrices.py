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
    
    #Make sure genes equal each other 
    #-------------------------------------------------
    assert set(df1.gene.unique()) == set(df2.gene.unique()), 'The two count matrices have different genes.'
    #-------------------------------------------------

    # Add position string 
    #-------------------------------------------------
    pos_string_to_add = '_pos_'+ count_matrix_src.split('Pos')[1].split('/Segmentation')[0]
    df2.columns = df2.columns + pos_string_to_add
    #-------------------------------------------------

    #Add horizontally
    #-------------------------------------------------
    combined_df = pd.concat([df1, df2.drop(columns=['gene'+ pos_string_to_add], axis = 1)], axis=1)
    #-------------------------------------------------
    
    return combined_df
    
    
def get_initial_count_matrix(all_count_matrices):
    
    #Make initial count matrix
    #----------------------------------------
    comb_count_matrices = pd.read_csv(all_count_matrices[0])
    pos_string_to_add = '_pos_'+ all_count_matrices[0].split('Pos')[1].split('/Segmentation')[0]
    comb_count_matrices.columns = comb_count_matrices.columns + pos_string_to_add
    comb_count_matrices = comb_count_matrices.rename(columns={"gene" + pos_string_to_add: "gene"})
    #----------------------------------------
    
    return comb_count_matrices
    

    
def get_count_matrix_for_pos(segment_dir, count_matrix_dst):

    glob_channel_count_matrices = os.path.join(segment_dir, 'Channel*', 'count_matrix.csv')
    
    count_matrix_src_s = glob.glob(glob_channel_count_matrices)
    
    comb_count_matrices = get_initial_count_matrix(count_matrix_src_s)
    print(f'{comb_count_matrices.shape=}')
    #Comebine all count matrices
    #----------------------------------------
    for i in range(1, len(count_matrix_src_s)):
        comb_count_matrices = combine_two_count_matrices(comb_count_matrices, count_matrix_src_s[i])
        print(f'{i=}')
        print(f'{comb_count_matrices.shape=}')
    #----------------------------------------
    
    #Save all combined count matrices
    #----------------------------------------
    comb_count_matrices.to_csv(count_matrix_dst, index=False)
    #----------------------------------------
    
if sys.argv[1] == 'debug':
    segment_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot_strict_1/MMStack_Pos7/Segmentation/'
    dst = 'foo.csv'
    
    get_count_matrix_for_pos(segment_dir, dst)