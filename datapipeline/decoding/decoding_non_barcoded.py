import os
import sys

import numpy as np
import pandas as pd


def locations_to_gene(df_codes, df_locs):
    genes_to_locs = []

    # Match genes to hybs and channels
    # --------------------------------------------------
    for hyb in df_codes.hyb.unique():
        for ch in df_codes.channel.unique():

            # Get Gene
            gene = df_codes[(df_codes.hyb == hyb) & \
                            (df_codes.channel == ch)]

            # See if gene is present and add
            if len(gene) > 0:
                df_locs.loc[(df_locs.hyb == hyb) & \
                            (df_locs.ch == ch), 'gene'] = gene.iloc[0, 0]

    # df_locs = df_locs.dropna()

    return df_locs


def run_decoding_non_barcoded(sequential_csv, locations_csv, position, dst_dir):
    # Read Barcodes and locations
    # --------------------------------------------------
    df_codes = pd.read_csv(sequential_csv)
    df_locs = pd.read_csv(locations_csv)
    # --------------------------------------------------

    # Get Genes from dots
    # --------------------------------------------------
    df_locs["gene"] = np.nan
    df_decoded = locations_to_gene(df_codes, df_locs)
    # --------------------------------------------------

    # Save Decoded Genes
    # --------------------------------------------------
    df_decoded.to_csv(os.path.join(dst_dir, 'sequential_decoding_results.csv'), index=False)
    print(f'{dst_dir=}')
    # --------------------------------------------------

    return df_decoded


if __name__ == '__main__':

    if sys.argv[1] == 'debug_smfish_decoding':
        dst_dir = 'foo/smfish_test'
        os.makedirs(dst_dir, exist_ok=True)
        df_decoded = run_decoding_non_barcoded(
            sequential_csv='/groups/CaiLab/personal/nrezaee/raw/test1-big/non_barcoded_key/sequential_key.csv',
            locations_csv='/groups/CaiLab/analyses/nrezaee/test1-big/non_barcoded/MMStack_Pos0/Dot_Locations/locations.csv',
            position=0,
            dst_dir=dst_dir)

    if sys.argv[1] == 'debug_smfish_decoding_anthony':
        dst_dir = 'foo/smfish_test_anthony'
        os.makedirs(dst_dir, exist_ok=True)
        df_decoded = run_decoding_non_barcoded(
            sequential_csv='/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013/non_barcoded_key/sequential_key.csv',
            locations_csv='/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Dot_Locations/locations.csv',
            position=0,
            dst_dir=dst_dir)

    if sys.argv[1] == 'debug_smfish_decoding_michal':
        dst_dir = 'foo/smfish_test_michal'
        os.makedirs(dst_dir, exist_ok=True)
        df_decoded = run_decoding_non_barcoded(
            sequential_csv='/groups/CaiLab/analyses/Michal/2021-06-21_Neuro4181_5_noGel_cellMarkers/test_pos33_strict7_channel2_1/BarcodeKey/sequential_key.csv',
            locations_csv='/groups/CaiLab/analyses/Michal/2021-06-21_Neuro4181_5_noGel_cellMarkers/test_pos33_strict7_channel2_1/MMStack_Pos33/Dot_Locations/locations.csv',
            position=0,
            dst_dir=dst_dir)
