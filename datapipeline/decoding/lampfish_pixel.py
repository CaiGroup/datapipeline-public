import json
import os
import random
import string
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.registration import phase_cross_correlation

from .lampfish_helpers.lampfish_funcs import get_hyb_dirs, get_loaded_tiff, get_pixels
from ..load_tiff import tiffy


def get_channel_offsets(tiff_dir, position, dst, num_wav):
    """
    Get offset channel by channel 
    """

    # Get path for each hyb dir
    # ---------------------------------------------------------------
    hyb_dirs = get_hyb_dirs(tiff_dir)
    print(f'{hyb_dirs=}')
    # ---------------------------------------------------------------

    # Get Offset for each hyb dir
    # ---------------------------------------------------------------
    offsets = {}
    for hyb_dir in hyb_dirs:
        tiff_src = os.path.join(hyb_dir, position)
        tiff = tiffy.load(tiff_src, num_wav=num_wav)
        shift, error, diffphase = phase_cross_correlation(tiff[0], tiff[1], upsample_factor=100)
        print(f'{shift=}')
        offsets[tiff_src] = shift.tolist()
    # ---------------------------------------------------------------

    # Save Offsets
    # ---------------------------------------------------------------
    with open(dst, "w") as outfile:
        json.dump(offsets, outfile)
    # ---------------------------------------------------------------


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def plot_img(img, x_s, y_s, hyb):
    plt.figure(figsize=(40, 40))
    plt.imshow(img, cmap='gray')
    plt.scatter(np.array(x_s) - .5, np.array(y_s) - .5, s=.1, color='r')

    temp_dir = 'check_imgs_pos' + str(pos)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    plt.savefig(os.path.join(temp_dir, 'Hyb_' + str(hyb) + '.png'))


# def get_pixels(tiff_3d, df_locs, offset, hyb):

#     #Add offset to points
#     #---------------------------------------------------------------
#     intensity_3_by_3 = []
#     x_s = list(df_locs.x - offset[2])
#     y_s = list(df_locs.y - offset[1])
#     z_s = list(df_locs.z - offset[0]) 
#     ints = list(df_locs.int)
#     #---------------------------------------------------------------

#     #Get 3x3 of of points in ch1
#     #---------------------------------------------------------------
#     for i in range(df_locs.shape[0]):
#         intensity = tiff_3d[np.round(z_s).astype(np.int16), np.round(y_s[i]).astype(np.int16), np.round(x_s[i]).astype(np.int16)]

#         intensity_3_by_3.append(intensity)

#     df_locs['sum_3x3_int_ch1'] = intensity_3_by_3
#     df_locs['hyb'] = np.full((df_locs.shape[0]), hyb)
#     return df_locs

# Set Position
def get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst, num_wav):
    # Get Offset across Hybs
    # ---------------------------------------------------------------
    with open(offsets_src) as json_file:
        offsets = json.load(json_file)
    # ---------------------------------------------------------------

    # Get locations csv
    # ---------------------------------------------------------------
    df_locs = pd.read_csv(locations_src)
    print(f'{df_locs=}')
    df_new_locs = pd.DataFrame(columns=['hyb', 'ch', 'x', 'y', 'z', 'int', 'sum_3x3_int_ch1'])
    # ---------------------------------------------------------------

    # Go through Each Hyb
    # ---------------------------------------------------------------
    position = 'MMStack_Pos' + str(pos) + '.ome.tif'
    hyb_dirs = get_hyb_dirs(tiff_dir)
    for hyb in df_locs.hyb.unique():
        # Load the tiff
        # ---------------------------------------------------------------
        tiff, tiff_src = get_loaded_tiff(hyb_dirs, position, hyb, num_wav=num_wav)
        tiff_ch = tiff[:, 0, :, :]
        # ---------------------------------------------------------------

        # Get right locations and offset
        # ---------------------------------------------------------------
        df_hyb_ch = df_locs[(df_locs.hyb == df_locs.hyb.min()) & (df_locs.ch == 1)]
        offset = offsets[(os.sep).join(tiff_src.split(os.sep)[-2:])]
        # ---------------------------------------------------------------

        # Get the 3x3 column
        # ---------------------------------------------------------------
        df_new_locs = df_new_locs.append(get_pixels(tiff_ch, df_hyb_ch, offset, hyb, new_col_name='sum_3x3_int_ch1'))
        print(f'{df_new_locs.shape=}')
        # ---------------------------------------------------------------

    # Save dataframe to csv
    # ---------------------------------------------------------------
    df_new_locs.to_csv(dst, index=False)
    # ---------------------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_lampfish_ch1':
        pos = 0
        offsets_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/offsets.json'
        locations_src = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos_strict_8/MMStack_Pos1/Dot_Locations/locations.csv'
        tiff_dir = '/groups/CaiLab/personal/Linus/raw/5ratiometric_test'
        get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos,
                                dst='foo/lampfish_decoding_ch1.csv' + str(pos) + '.csv')

    elif sys.argv[1] == 'debug_lampfish_ch1_test1':
        pos = 0
        offsets_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/offsets.json'
        locations_src = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/Dot_Locations/locations.csv'
        tiff_dir = '/groups/CaiLab/personal/nrezaee/raw/test1'
        get_ratio_first_channel(offsets_src, locations_src, tiff_dir, pos, dst='foo/lampfish_decoding__test_ch1.csv',
                                num_wav=4)
