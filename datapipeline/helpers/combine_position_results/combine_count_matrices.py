import glob
import os
import sys

import numpy as np
import pandas as pd


def combine_two_count_matrices(df1, count_matrix_src):
    """
    Combine two count matrices
    """

    df2 = pd.read_csv(count_matrix_src)

    # Get Differences in Count Matrices
    # -------------------------------------------------
    not_in_df2 = np.setdiff1d(df1.gene.unique(), df2.gene.unique())
    not_in_df1 = np.setdiff1d(df2.gene.unique(), df1.gene.unique())
    # -------------------------------------------------

    # Put Missing Genes in df2
    # -------------------------------------------------
    for missing_gene in not_in_df2:
        row_to_add = [missing_gene] + list(np.full((df2.shape[1] - 1), 0))
        df2.loc[len(df2)] = row_to_add
    # -------------------------------------------------

    # Put Missing Genes in df1
    # -------------------------------------------------
    for missing_gene in not_in_df1:
        row_to_add = [missing_gene] + list(np.full((df1.shape[1] - 1), 0))
        df1.loc[len(df1)] = row_to_add
    # -------------------------------------------------

    # Make sure genes equal each other
    # -------------------------------------------------
    assert set(df1.gene.unique()) == set(df2.gene.unique()), 'The two count matrices have different genes.'
    # -------------------------------------------------

    # Add position string 
    # -------------------------------------------------
    pos_string_to_add = '_pos_' + count_matrix_src.split('Pos')[1].split('/Segmentation')[0]
    df2.columns = df2.columns + pos_string_to_add
    # -------------------------------------------------

    # Add horizontally
    # -------------------------------------------------
    combined_df = pd.concat([df1, df2.drop(columns=['gene' + pos_string_to_add], axis=1)], axis=1)
    # -------------------------------------------------

    return combined_df


def get_all_dirs_with_count_matrices(analysis_dir):
    # Get All Dirs with count Matrices
    # ----------------------------------------
    # For Individual decoding
    glob_me_for_seg_dirs = os.path.join(analysis_dir, 'MMStack_Pos*', 'Segmentation')
    print(f'{glob_me_for_seg_dirs=}')
    all_seg_dirs = glob.glob(glob_me_for_seg_dirs)
    # ----------------------------------------

    return all_seg_dirs


def add_count_matrix_to_end_of_path(all_seg_dirs):
    # Get All count_matrices
    # ----------------------------------------
    assert len(all_seg_dirs) > 0, "There were no count matrices found."
    all_count_matrices = [os.path.join(seg_dir, 'count_matrix_all_channels.csv') for seg_dir in all_seg_dirs]

    for count_matrix in all_count_matrices:
        assert os.path.isfile(count_matrix), 'One of the count matrices is missing.'
    # ----------------------------------------

    return all_count_matrices


def get_initial_count_matrix(all_count_matrices):
    # Make initial count matrix
    # ----------------------------------------
    comb_count_matrices = pd.read_csv(all_count_matrices[0])
    pos_string_to_add = '_pos_' + all_count_matrices[0].split('Pos')[1].split('/Segmentation')[0]
    comb_count_matrices.columns = comb_count_matrices.columns + pos_string_to_add
    comb_count_matrices = comb_count_matrices.rename(columns={"gene" + pos_string_to_add: "gene"})
    # ----------------------------------------

    return comb_count_matrices


def get_combined_count_matrix(analysis_dir, dst):
    """
    Combine all count matrices for all positions
    """

    # Make directory in case, and make sure analysis exists
    # ----------------------------------------
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    assert os.path.exists(analysis_dir), 'The analysis directory does not exist.'
    # ----------------------------------------

    # Get all seg dirs
    # ----------------------------------------
    all_seg_dirs = get_all_dirs_with_count_matrices(analysis_dir)
    # ----------------------------------------

    # Count matrix to end
    # ----------------------------------------
    all_count_matrices = add_count_matrix_to_end_of_path(all_seg_dirs)
    print(f'{all_count_matrices=}')
    # ----------------------------------------

    # Get initial count matrix
    # ----------------------------------------
    comb_count_matrices = get_initial_count_matrix(all_count_matrices)
    # ----------------------------------------

    # Comebine all count matrices
    # ----------------------------------------
    for i in range(1, len(all_count_matrices)):
        comb_count_matrices = combine_two_count_matrices(comb_count_matrices, all_count_matrices[i])
        print(f'{i=}')
        print(f'{comb_count_matrices.shape=}')
    # ----------------------------------------

    # Save all combined count matrices
    # ----------------------------------------
    comb_count_matrices.to_csv(dst, index=False)
    # ----------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_comb_count_matrices':
        analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_2_pos_2_chs_pil_load_strict_2_only_blur_thresh_60'
        dst = 'foo/foo.csv'

        get_combined_count_matrix(analysis_dir, dst)
