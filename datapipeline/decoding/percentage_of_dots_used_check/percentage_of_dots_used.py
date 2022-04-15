import os
import sys

import pandas as pd


def get_percentage_of_dots_used(locs_src, decoded_genes_src, channel, dst_dir):
    # Open locations and decoded genes
    # ----------------------------------------------------
    df_locs = pd.read_csv(locs_src)
    df_locs_ch = df_locs[df_locs.ch == channel]
    df_genes = pd.read_csv(decoded_genes_src)
    # ----------------------------------------------------

    # Get percentage of dots used
    # ----------------------------------------------------
    percentage_of_used_dots = ((df_genes.shape[0] * 4) / df_locs.shape[0]) * 100
    # ----------------------------------------------------

    # Write to file
    # ----------------------------------------------------
    dst = os.path.join(dst_dir, 'percentage_of_dots_used.txt')
    print(f'{dst=}')
    file1 = open(dst, "w")
    line_to_write = 'Percentage of Dots Used ' + str(round(percentage_of_used_dots, 2)) + '%'
    file1.write(line_to_write)
    file1.close()
    # ----------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_percent_of_dots_used':
        get_percentage_of_dots_used(
            locs_src='/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/Dot_Locations/locations.csv',
            decoded_genes_src='/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/Decoded/Channel_1/pre_seg_diff_1_minseeds_3_unfiltered.csv', \
            channel=1,
            dst_dir=os.path.dirname(
                '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/Decoded/Channel_1/pre_seg_diff_1_minseeds_3_unfiltered.csv'))
