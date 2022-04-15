import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_on_off_barcode_plot_all_pos(combined_count_matrix_src, png_dst):
    os.makedirs(os.path.dirname(png_dst), exist_ok=True)

    df_count_matrix = pd.read_csv(combined_count_matrix_src)

    # Get dictionary of counts for each gene
    # ------------------------------------------------------
    df_count_matrix = df_count_matrix.set_index('gene')
    dict_gene_counts = df_count_matrix.sum(axis=1).to_dict()
    # ------------------------------------------------------

    # Get all real and fake counts
    # ------------------------------------------------------
    real_counts = []
    fake_counts = []
    for key in dict_gene_counts.keys():
        if 'fake' in key:
            fake_counts.append(dict_gene_counts[key])
        else:
            real_counts.append(dict_gene_counts[key])

    print(f'{len(real_counts)=}')
    print(f'{len(fake_counts)=}')
    real_counts = sorted(real_counts, reverse=True)
    fake_counts = sorted(fake_counts, reverse=True)
    # ------------------------------------------------------

    # Plot the figure
    # ------------------------------------------------------
    plt.figure(figsize=(8, 6))

    plt.title('On/Off Sorted Barcode Counts', fontsize=23)

    num_cells = 1

    plt.ylabel('Counts of Genes', fontsize=18)
    plt.xlabel('Sorted Barcodes', fontsize=18)
    plt.plot(np.array(real_counts) / num_cells)
    x_points_for_fake = range(len(real_counts), len(real_counts) + len(fake_counts))
    plt.plot(x_points_for_fake, np.array(fake_counts))

    plt.savefig(png_dst)
    # ------------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_on_off_plot_all_pos':
        combined_count_matrix_src = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos11/Segmentation/count_matrix_all_channels.csv'
        png_dst = 'foo/on_off_all_chs.png'

        get_on_off_barcode_plot_all_pos(combined_count_matrix_src, png_dst)
