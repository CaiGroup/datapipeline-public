import glob
import os
import sys

import pandas as pd


def add_ch_to_fake_genes(df_count_matrix, count_matrix_src):
    # Get Channel
    # ----------------------------------------------
    print(f'{count_matrix_src=}')
    channel = count_matrix_src.split(os.sep)[-2].split('Channel_')[1]
    # ----------------------------------------------

    # Loop through and add channel to fakes
    # ----------------------------------------------
    genes_with_fake_chs = []
    for gene in list(df_count_matrix.gene):

        if 'fake' in gene:
            genes_with_fake_chs.append(gene + '_ch_' + channel)
        else:
            genes_with_fake_chs.append(gene)
    # ----------------------------------------------

    # Save count matrix genes with ch
    # ----------------------------------------------
    df_count_matrix.gene = genes_with_fake_chs
    # ----------------------------------------------

    return df_count_matrix


def combine_two_count_matrix_channels_in_position(df_count1, count_matrix_src2):
    # Read in count matrices
    # ----------------------------------------------
    df_count2 = pd.read_csv(count_matrix_src2)
    print(f'{df_count2.shape=}')
    # ----------------------------------------------

    # Add channels to fakes
    # ----------------------------------------------
    df_count2 = add_ch_to_fake_genes(df_count2, count_matrix_src2)
    # ----------------------------------------------

    # Add count matrices
    # ----------------------------------------------
    df_combed_count = df_count1.append(df_count2)
    print(f'{df_combed_count.shape=}')
    # ----------------------------------------------

    return df_combed_count


def get_count_matrix_for_pos(segment_dir, dst):
    # Get All count matrices in position
    # --------------------------------------------------
    glob_me_for_count_matrices = os.path.join(segment_dir, 'Channel_*', 'count_matrix.csv')
    count_matrix_src_s_in_pos = glob.glob(glob_me_for_count_matrices)
    # --------------------------------------------------

    # Set first count matrix
    # --------------------------------------------------
    df_combined_count = pd.read_csv(count_matrix_src_s_in_pos[0])
    df_combined_count = add_ch_to_fake_genes(df_combined_count, count_matrix_src_s_in_pos[0])
    # --------------------------------------------------

    # Loop through and append count_matrices
    # --------------------------------------------------
    for count_matrix_src in count_matrix_src_s_in_pos[1:]:
        df_combined_count = combine_two_count_matrix_channels_in_position(df_combined_count, count_matrix_src)
    # --------------------------------------------------

    df_combined_count.to_csv(dst, index=False)


if __name__ == '__main__':

    if sys.argv[1] == 'debug_comb_count_matrix_channels':
        count_matrix_src1 = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos10/Segmentation/Channel_2/count_matrix.csv'
        count_matrix_src2 = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos10/Segmentation/Channel_1/count_matrix.csv'

        count_matrix_dst = 'foo.csv'

        combine_count_matrix_channels_in_position(count_matrix_src1, count_matrix_src2, count_matrix_dst)
        print(f'{count_matrix_dst=}')

    if sys.argv[1] == 'debug_comb_all_count_matrix_channels':
        pos_analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos2/Segmentation'
        dst = 'foo2.csv'
        get_count_matrix_for_pos(pos_analysis_dir, dst)
