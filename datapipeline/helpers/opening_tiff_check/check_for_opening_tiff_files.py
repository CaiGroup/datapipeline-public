import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from ...load_tiff import tiffy


def get_plots_of_tiff_check(tiff_src, num_wav, dest=None):
    # Read in tiff file
    # --------------------------------------------
    tiff = tiffy.load(tiff_src, num_wav, dest)
    print(f'{tiff.shape=}')
    # --------------------------------------------

    # Plot subplots of tiff
    # --------------------------------------------
    fig, axs = plt.subplots(tiff.shape[1], tiff.shape[0], figsize=(15, 15))
    for ch in range(tiff.shape[1]):
        for z in range(tiff.shape[0]):
            # axs[ch, z].set_title('Channel ' + str(ch) + ' Z ' + str(z))
            if tiff.shape[0] > 1:
                axs[ch, z].imshow(np.log(tiff[z, ch]), cmap='gray')
            else:
                axs[ch].imshow(np.log(tiff[z, ch]), cmap='gray')
    # --------------------------------------------

    # Label Rows and columns
    # --------------------------------------------
    if tiff.shape[0] > 1:
        rows = ['Channel {}'.format(col) for col in range(1, tiff.shape[1] + 1)]
        cols = ['Z {}'.format(row) for row in range(1, tiff.shape[0] + 1)]

        for ax, col in zip(axs[0], cols):
            ax.set_title(col)

        for ax, row in zip(axs[:, 0], rows):
            ax.set_ylabel(row, rotation=0, size='large')
    # --------------------------------------------

    if dest != None:
        # Save subplots
        # --------------------------------------------
        fig.savefig(dest)
        print(f'{dest=}')
        # --------------------------------------------


def get_opening_tiff_check(data_dir, position, num_wav, dest):
    # Make directory that dest is in
    # --------------------------------------------
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # --------------------------------------------

    # Get Tiff File for check
    # --------------------------------------------
    glob_me_for_tiff_files = os.path.join(data_dir, 'HybCycle_*', position)
    print(f'{glob_me_for_tiff_files=}')
    tiff_files_for_pos = glob.glob(glob_me_for_tiff_files)

    assert len(tiff_files_for_pos) > 0, 'There are no tiff files found.'

    tiff_for_check_src = tiff_files_for_pos[0]
    # --------------------------------------------

    # Get Plots for tiff check
    # --------------------------------------------
    get_plots_of_tiff_check(tiff_for_check_src, num_wav, dest)
    # --------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_plot_from_tiff_src':
        tiff_src = '/groups/CaiLab/personal/Yodai/raw/2021-03-30-E14-100k-DNAfull-rep2-laminB1-H3K27me3-DAPI-H4K20me3/HybCycle_0/MMStack_Pos0.ome.tif'
        dest = 'foo2.png'
        num_wav = 4

        get_plots_of_tiff_check(tiff_src, num_wav, dest)

    if sys.argv[1] == 'debug_tiff_check':
        data_dir = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei'
        position = 'MMStack_Pos0.ome.tif'
        dest = 'foo/foo.png'

        get_opening_tiff_check(data_dir, position, dest)

    if sys.argv[1] == 'debug_tiff_check_1z':
        data_dir = '/groups/CaiLab/personal/Michal/raw/2021-06-21_Neuro4181_5_noGel_cellMarkers'
        position = 'MMStack_Pos0.ome.tif'
        dest = 'foo/foo_1z.png'

        get_opening_tiff_check(data_dir, position, dest)
