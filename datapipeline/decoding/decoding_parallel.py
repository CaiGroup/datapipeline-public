import os
import subprocess
import sys
import time
import random

import numpy as np
import pandas as pd
from scipy.io import loadmat

debug = False

from .helpers.parallel.seg_locs import get_segmentation_dict_dots
from .helpers.parallel.rand_list import are_jobs_finished, get_squeue_output, get_random_list
from .helpers.parallel.combine_csv_s import get_combined_csv


def get_barcode_info(barcode_src):
    print("Reading Barcode Key")

    barcodes = loadmat(barcode_src)["barcodekey"]

    num_of_rounds = barcodes[0][0][0].shape[1]

    channels_per_round = np.max(barcodes[0][0][0][:200])

    total_number_of_channels = num_of_rounds * channels_per_round

    print(f'{channels_per_round=}')
    print(f'{total_number_of_channels=}')
    print(f'{num_of_rounds=}')
    assert total_number_of_channels % num_of_rounds == 0

    return total_number_of_channels, num_of_rounds


def run_matlab_decoding(rand, barcode_src, locations_cell_path, dest, num_of_rounds, allowed_diff, min_seeds,
                        total_number_of_channels, channel_index, number_of_individual_channels_for_decoding):
    print(f'{barcode_src=}')
    print(f'{locations_cell_path=}')
    # Create Matlab Command
    # -------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """

    folder = os.path.dirname(__file__)
    decoding_dir = os.path.join(folder, 'helpers')

    if channel_index == None and number_of_individual_channels_for_decoding == None:

        print(f'{min_seeds=}')

        cmd = cmd.format(decoding_dir, barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels,
                         '[]', '[]', allowed_diff, min_seeds)

        print(f'{cmd=}')
    else:

        print(f'{type(channel_index)=}')
        print(f'{type(number_of_individual_channels_for_decoding)=}')

        print(f'{channel_index=}')
        print(f'{number_of_individual_channels_for_decoding=}')

        cmd = cmd.format(decoding_dir, barcode_src, locations_cell_path, dest, num_of_rounds, total_number_of_channels, \
                         channel_index + 1, number_of_individual_channels_for_decoding, allowed_diff, min_seeds)

    # -------------------------------------------------------------------

    script_name = os.path.join(dest, 'decoding.sh')
    with open(script_name, 'w') as f:
        f.write('#!/bin/bash \n')
        f.write(cmd)

    output_path = os.path.join(dest, 'slurm_decoding.out')

    call_me = [
        'sbatch',
        '--begin', 'now+120',
        '--job-name', rand,
        "--output", output_path,
        "--time", "0:50:00",
        "--mem-per-cpu", "8G",
        '--ntasks', '1', script_name
    ]

    print(" ".join(call_me))
    subprocess.call(call_me)


def save_points_int_to_csv(points, intensities, csv_dst):
    df = pd.DataFrame(columns=['hyb', 'ch', 'x', 'y', 'z', 'int'])

    for i in range(points.shape[0]):
        hyb_array = np.full((points[i].shape[0]), i)
        ch_array = np.full((points[i].shape[0]), 1)
        data_for_df = {'hyb': hyb_array, 'ch': ch_array, \
                       'x': np.squeeze(points[i][:, 0]), 'y': np.squeeze(points[i][:, 1]), \
                       'z': np.squeeze(points[i][:, 2]), 'int': np.squeeze(intensities[i])}
        df_ch = pd.DataFrame(data_for_df)

        df = df.append(df_ch)

    df.to_csv(csv_dst, index=False)

    return None


def decoding(barcode_src, locations_src, labeled_img, dest, allowed_diff, min_seeds, channel_index=None, \
             number_of_individual_channels_for_decoding=None, roi_path=None, decode_only_cells=False, start_time=None):
    print(f'{barcode_src=}')
    print(f'{locations_src=}')
    print(f'{labeled_img.shape=}')

    print(f'{channel_index=}')
    print(f'{number_of_individual_channels_for_decoding=}')

    total_number_of_channels, num_of_rounds = get_barcode_info(barcode_src)

    plotted_img_dest = os.path.join(dest, 'Plotted_Cell_Spot_Locations.png')
    seg_dict = get_segmentation_dict_dots(locations_src, labeled_img, plotted_img_dest)

    rand_list = get_random_list(len(seg_dict.keys()))

    cell_dirs = []

    if decode_only_cells == True:
        start_cell = 1
    else:
        start_cell = 0

    last_cell = len(seg_dict.keys())

    # Sleep a random amount of time to stagger other positions'
    # submissions of many jobs. This is bad.
    random_sleep = random.randrange(1, 50, 1)
    time.sleep(random_sleep)
    # Check how many jobs we currently have running to see if we need to sleep
    # before submitting more
    def len_squeue_output():
        squeue_lines = get_squeue_output().split()
        return len(squeue_lines)

    while len_squeue_output() > 7500:
        print('Too many jobs, waiting...')
        time.sleep(60 * 20)

    for i in range(start_cell, last_cell):
        print("Saving locations")
        # Get and Save Location in Dict Key
        # -------------------------------------------------------------------
        locations_for_cell = np.array(seg_dict[list(seg_dict.keys())[i]])

        cell_dirs.append('cell_' + str(i))
        temp_dir = os.path.join(dest, 'cell_' + str(i))
        os.makedirs(temp_dir, exist_ok=True)
        locations_cell_path = os.path.join(temp_dir, 'locations_for_cell.csv')

        save_points_int_to_csv(locations_for_cell[:, 0], locations_for_cell[:, 1], locations_cell_path)

        # savemat(locations_cell_path, {'points':locations_for_cell[:,0], 'intensity':locations_for_cell[:,1]})
        temp_dest = temp_dir
        # -------------------------------------------------------------------

        run_matlab_decoding(rand_list[i], barcode_src, locations_cell_path, temp_dest, num_of_rounds, allowed_diff,
                            min_seeds, total_number_of_channels, channel_index,
                            number_of_individual_channels_for_decoding)

    # Check if Jobs are Finished
    # -----------------------------------------------------------------------------
    while not are_jobs_finished(rand_list):
        print(f'Waiting for Decoding Jobs to Finish')
        time.sleep(10)

    print(f'{rand_list=}')
    # -----------------------------------------------------------------------------

    if min_seeds == 'number_of_rounds - 1':
        min_seeds = num_of_rounds - 1

    dest_unfilt = os.path.join(dest,
                               'pre_seg_diff_' + str(allowed_diff) + '_minseeds_' + str(min_seeds) + '_unfiltered.csv')
    dest_filt = os.path.join(dest,
                             'pre_seg_diff_' + str(allowed_diff) + '_minseeds_' + str(min_seeds) + '_filtered.csv')
    print(f'{dest_filt=}')
    get_combined_csv(dest, cell_dirs, dest_unfilt, dest_filt)

    return dest_unfilt


if __name__ == '__main__':

    if sys.argv[1] == 'debug_parallel':
        import tifffile

        labeled_img_src = '/groups/CaiLab/analyses/Michal/2021-06-21_Neuro4181_5_noGel_pool1/test_strict7_pos33_channel1/MMStack_Pos33/Segmentation/labeled_img.tif'
        barcode_src = '/groups/CaiLab/analyses/Michal/2021-06-21_Neuro4181_5_noGel_pool1/test_strict7_pos33_channel1/BarcodeKey/channel_1.mat'
        locations_src = '/groups/CaiLab/analyses/Michal/2021-06-21_Neuro4181_5_noGel_pool1/test_strict7_pos33_channel1/MMStack_Pos33/Dot_Locations/locations.csv'

        dest = '/home/lombelet/test_cronjob_multi_dot/foo/test'
        if not os.path.exists(dest):
            os.makedirs(dest)
        allowed_diff = 1
        min_seeds = 3

        labeled_img = tifffile.imread(labeled_img_src)
        decoding(barcode_src, locations_src, labeled_img, dest, allowed_diff, min_seeds, channel_index=0, \
                 number_of_individual_channels_for_decoding=1)
