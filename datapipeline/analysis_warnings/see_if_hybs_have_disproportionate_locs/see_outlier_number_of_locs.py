import glob
import os
import sys

import pandas as pd


def get_hybs_with_low_number_of_dots(locs_src, times_less_than=5):
    # Read in locations
    # ----------------------------------------------------------
    df_locs = pd.read_csv(locs_src)
    # ----------------------------------------------------------

    # Get the number of dots for each hyb and ch
    # ----------------------------------------------------------
    df_n_dots = pd.DataFrame(columns=['hyb', 'ch', 'n_dots'])
    for hyb in df_locs.hyb.unique():
        for ch in df_locs.ch.unique():
            df_hyb_ch = df_locs[(df_locs.hyb == hyb) & (df_locs.ch == ch)]
            df_n_dots = df_n_dots.append({'hyb': hyb, 'ch': ch, 'n_dots': df_hyb_ch.shape[0]}, ignore_index=True)
    # ----------------------------------------------------------

    df_hybs_with_little_dots = df_n_dots[df_n_dots['n_dots'] < (df_n_dots.n_dots.max() / times_less_than)]

    # Add position column
    # ----------------------------------------------------------
    pos = locs_src.split('MMStack_Pos')[1].split('/Dot_Locations')[0]
    df_hybs_with_little_dots['pos'] = pos
    # ----------------------------------------------------------

    return df_hybs_with_little_dots


def get_lines_to_write_from_df(df):
    # Iterate and get lines to write
    # --------------------------------------------
    channels_to_write_to_file = []
    for index, row in df.iterrows():
        line_to_write = '        Pos ' + str(row.pos) + ' HybCycle ' + str(row.hyb) + ' Channel ' + str(
            row.ch) + ' only has ' + str(row.n_dots) + ' dots \n'
        channels_to_write_to_file.append(line_to_write)
    # --------------------------------------------

    return channels_to_write_to_file


def write_disproporionate_number_of_dots_to_file_for_one_pos(warnings_src, locations_src):
    # Get Dataframe with channels with lowest dots
    # --------------------------------------------
    df_hybs_with_little_dots = get_hybs_with_low_number_of_dots(locs_src, times_less_than=2)
    # --------------------------------------------

    # Get Channels to write
    # --------------------------------------------
    channels_to_write_to_file = get_lines_to_write_from_df(df_hybs_with_little_dots)
    # --------------------------------------------

    # Write to file
    # --------------------------------------------
    warnings_file = open(warnings_src, 'a+')
    warnings_file.write('Dot Detection Issues \n')

    warnings_file.write('    Few Dots in These Channels \n')
    if len(channels_to_write_to_file) > 0:
        warnings_file.writelines(channels_to_write_to_file)
    else:
        warnings_file.write('        None \n')

    warnings_file.close()
    # --------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_warnings_outlier_number_of_dots':
        locs_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_debug3_pos8_strict15_ch2/MMStack_Pos13/Dot_Locations/locations.csv'
        warnings_src = 'foo.txt'

        write_disproporionate_number_of_dots_to_file_for_one_pos(warnings_src, locs_src)


def write_disproporionate_number_of_dots_to_file_for_all_pos(warnings_src, analysis_dir):
    # Get all location files
    # --------------------------------------------
    glob_me_for_all_pos_files = os.path.join(analysis_dir, 'MMStack_Pos*', 'Dot_Locations', 'locations.csv')
    all_loc_files = glob.glob(glob_me_for_all_pos_files)
    # --------------------------------------------

    # Loop through to get all positions with little dots
    # --------------------------------------------
    df_all_pos_small_n_dots = pd.DataFrame(columns=['hyb', 'ch', 'n_dots', 'pos'])
    for loc_file in all_loc_files:
        df_hybs_with_little_dots = get_hybs_with_low_number_of_dots(loc_file, times_less_than=3)
        df_all_pos_small_n_dots = df_all_pos_small_n_dots.append(df_hybs_with_little_dots)
    # --------------------------------------------

    # Get Channels to write
    # --------------------------------------------
    channels_to_write_to_file = get_lines_to_write_from_df(df_all_pos_small_n_dots)
    # --------------------------------------------

    # Write to file
    # --------------------------------------------
    warnings_file = open(warnings_src, 'a+')
    warnings_file.write('Dot Detection Issues \n')

    warnings_file.write('    Few Dots in These Channels \n')
    if len(channels_to_write_to_file) > 0:
        warnings_file.writelines(channels_to_write_to_file)
    else:
        warnings_file.write('        None \n')

    warnings_file.close()
    # --------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_warnings_outlier_number_of_dots_all_pos':
        analysis_dir = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_debug3_pos8_strict15_ch2/'
        warnings_src = 'foo.txt'

        write_disproporionate_number_of_dots_to_file_for_all_pos(warnings_src, analysis_dir)
