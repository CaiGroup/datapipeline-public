import glob
import os
import sys

import pandas as pd


def combine_two_locs_csv_s(df_all_pos, csv_2):
    df_locs_2 = pd.read_csv(csv_2)
    print(f'{df_locs_2.shape=}')
    df_locs_2['pos'] = int(csv_2.split('MMStack_Pos')[1].split('/Dot_Locations/locations.csv')[0])

    df_comb_locs = df_all_pos.append(df_locs_2)

    return df_comb_locs


def combine_locs_csv_s(analysis_dir):
    # Get all position locations csv's
    glob_me = os.path.join(analysis_dir, 'MMStack_Pos*', 'Dot_Locations', 'locations.csv')
    pos_locs_csv = glob.glob(glob_me)
    print(f'{pos_locs_csv=}')

    df_all_pos = pd.read_csv(pos_locs_csv[0])
    df_all_pos['pos'] = int(pos_locs_csv[0].split('MMStack_Pos')[1].split('/Dot_Locations/locations.csv')[0])
    for i in range(1, len(pos_locs_csv)):
        df_all_pos = combine_two_locs_csv_s(df_all_pos, pos_locs_csv[i])
        print(f'{df_all_pos.shape=}')

    df_all_pos_dst = os.path.join(analysis_dir, 'All_Positions', 'Dot_Locations', 'all_pos_locations.csv')
    os.makedirs(os.path.dirname(df_all_pos_dst), exist_ok=True)
    print(f'{df_all_pos_dst=}')
    df_all_pos.to_csv(df_all_pos_dst, index=False)


if __name__ == '__main__':

    if sys.argv[1] == 'debug_comb_pos_locs':
        analysis_dir = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/'
        combine_locs_csv_s(analysis_dir)
