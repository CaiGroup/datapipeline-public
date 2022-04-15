from __future__ import annotations

import os
import tempfile
import warnings
from typing import Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from skimage.feature import blob_log

from datapipeline.dot_detection.dot_detectors_3d.ilastik_3d_by_channel import run_back_sub
from datapipeline.dot_detection.helpers.add_z import add_z_col
from datapipeline.dot_detection.helpers.background_subtraction import get_background
from datapipeline.dot_detection.helpers.compile_dots import add_to_dots_in_channel
from datapipeline.dot_detection.helpers.shift_locations import shift_locations
from datapipeline.dot_detection.helpers.threshold import apply_thresh
from datapipeline.dot_detection.helpers.visualize_dots import get_visuals
from datapipeline.load_tiff import tiffy

warnings.filterwarnings("ignore")


def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel = tuple(np.array(tiff_2d.shape) // num_tiles)
    # print(f'{blur_kernel=}')
    blurry_img = cv2.blur(tiff_2d, blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)

    return tiff_2d


def adjust_tiles(tiff_3d):
    correct_me_z = createCLAHE(clipLimit=4, tileGridSize=(3, 3))
    for i in range(tiff_3d.shape[0]):
        tiff_3d[i] = correct_me_z.apply(tiff_3d[i])

    return tiff_3d


def blur_back_subtract_3d(tiff, num_tiles):
    for i in range(tiff.shape[0]):
        tiff[i, :, :] = blur_back_subtract(tiff[i, :, :], num_tiles)
    return tiff


def tophat_3d(tiff_3d):
    kernel = np.full((2, 2), 100)
    for i in range(tiff_3d.shape[0]):
        tiff_3d[i] = cv2.morphologyEx(tiff_3d[i], cv2.MORPH_TOPHAT, kernel)

    return tiff_3d


def process_for_dot_detection(tiff_3d, debug=False):
    tiff_3d = cv2.normalize(tiff_3d, None, 0, 500, norm_type=cv2.NORM_MINMAX).astype(np.uint16)
    blur_kernel = (600, 600)
    tiff_3d = blur_back_subtract_3d(tiff_3d, num_tiles=2)

    tiff_3d = cv2.normalize(tiff_3d, None, 0, 255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)

    tiff_3d = tophat_3d(tiff_3d)
    # tiff_3d = blur_back_subtract_3d(tiff_3d, num_tiles=2)

    tiff_3d = cv2.normalize(tiff_3d, None, 0, 20, norm_type=cv2.NORM_MINMAX).astype(np.uint8)

    return tiff_3d


def find_dots(chan_img: np.ndimage, intense_img) -> Tuple[np.ndarray, np.ndarray, int]:
    # Corresponds to a dot radius of sqrt(2)
    sigma = 2

    # Background subtraction with rolling ball radius of 3
    subtracted = chan_img

    # Run LoG dot finder
    log_result = blob_log(
        subtracted,
        min_sigma=sigma,
        max_sigma=sigma,
        num_sigma=1,
        threshold=0,
    )

    points = log_result[:, :2].astype(np.int64)
    intensities = intense_img.transpose()[points[:, 1], points[:, 0]]

    # Suggest dots brighter than 15th percentile of dot intensities
    # suggested_threshold = int(np.percentile(intensities, 15))

    return points, intensities  # , suggested_threshold


def find_dots_3d(tiff_3d, min_sigma=2, max_sigma=2, sigma_std=1, overlap=.2):
    # intens_img = get_tile_norms(tiff_3d, intens=True)
    tiff_3d_processed = process_for_dot_detection(tiff_3d)
    tiff_3d = blur_back_subtract_3d(tiff_3d, num_tiles=2)
    # tiff_3d_norm = cv2.normalize(tiff_3d, None, 0, 10, norm_type=cv2.NORM_MINMAX).astype(np.int16)
    dots_in_channel = None
    for z in range(tiff_3d.shape[0]):
        tiff_2d = tiff_3d_processed[z, :, :]

        # Get dots from 2d image
        # ---------------------------------------------------------------------
        dot_analysis = list(find_dots(tiff_2d, tiff_3d[z]))
        # ---------------------------------------------------------------------

        # Add Z column to dot locations
        # ---------------------------------------------------------------------
        dot_analysis = add_z_col(dot_analysis, z)
        # ---------------------------------------------------------------------

        # Switch [y, x, z] to [x, y, z]
        # ---------------------------------------------------------------------
        dot_analysis[0][:, [0, 1]] = dot_analysis[0][:, [1, 0]]
        # ---------------------------------------------------------------------

        dots_in_channel = add_to_dots_in_channel(dots_in_channel, dot_analysis)

    return dots_in_channel[0], dots_in_channel[1]


def run_inflect_all_channels(dots_in_tiff):
    print("Running Inflect all channels")
    print('-------------------------------------------------------------------------------------------------')

    # Getting INtensities
    intensities = [list(dots_in_channel[1]) for dots_in_channel in dots_in_tiff]

    # Making Temp dir
    temp_dir = tempfile.TemporaryDirectory()

    # Make intensity variables for command
    for intensity in intensities:
        # Make histogram
        # --------------------------------------------------------
        intensity = np.array(intensity)
        # w = 10
        # n = math.ceil((intensity.max() - intensity.min())/w)

        num_bins = 25

        bins = np.arange(np.min(intensity), np.max(intensity), (np.max(intensity) - np.min(intensity)) // num_bins)
        y, x, ignore = plt.hist(intensity, bins=bins, cumulative=-1)
        y = [int(i) for i in y]
        x = [int(i) for i in x][:-1]
        print(f'{y=}')
        print(f'{x=}')
        # --------------------------------------------------------

        # Declare y's
        # --------------------------------------------------------
        name_of_var_y = 'intensity_' + str(intensities.index(list(intensity))) + '_y'

        exec_var_command_y = name_of_var_y + " = " + str(y)
        # print(f'{exec_var_command_y=}')
        exec(exec_var_command_y)
        # --------------------------------------------------------

        # Declare x's
        # --------------------------------------------------------
        name_of_var_x = 'intensity_' + str(intensities.index(list(intensity))) + '_x'

        exec_var_command_x = name_of_var_x + " = " + str(x)
        # print(f'{exec_var_command_x=}')
        exec(exec_var_command_x)
        # --------------------------------------------------------

        # Declare Paths
        # --------------------------------------------------------
        dest = os.path.join(temp_dir.name, 'intensity_' + str(intensities.index(list(intensity))))

        custom_dest_name = 'intensity_' + str(intensities.index(list(intensity))) + '_path'
        exec_path_command = custom_dest_name + " =  '" + str(dest) + " ' "
        exec(exec_path_command)
        # --------------------------------------------------------

    # Run intensity vairables in command
    # --------------------------------------------------------
    path = os.path.join(os.path.dirname(__file__), 'inflection')
    cmd = "matlab -r " \
          "\"addpath('" + path + "');" \
                                 "knee_pt({0}, {1}, '{2}'); " \
                                 "knee_pt({3}, {4}, '{5}'); " \
                                 "knee_pt({6}, {7}, '{8}'); " \
                                 "quit\"; "

    cmd = cmd.format(locals()['intensity_0_y'], locals()['intensity_0_x'], locals()['intensity_0_path'], \
                     locals()['intensity_1_y'], locals()['intensity_1_x'], locals()['intensity_1_path'], \
                     locals()['intensity_2_y'], locals()['intensity_2_x'], locals()['intensity_2_path'])

    os.system(cmd)
    # --------------------------------------------------------

    # Get thresholds
    # --------------------------------------------------------
    inflect_threshs = []
    for i in range(len(intensities)):
        var_name_with_path = 'intensity_' + str(i) + '_path'
        res_x = loadmat(locals()[var_name_with_path])['res_x'][0]
        inflect_threshs.append(res_x)
    # --------------------------------------------------------

    # Threshold Values
    # --------------------------------------------------------
    for i in range(len(dots_in_tiff)):
        print("Length before", len(dots_in_tiff[i][1]))
        print(f'{inflect_threshs[i][0]=}')

        dots_in_tiff[i] = apply_thresh(dots_in_tiff[i], inflect_threshs[i][0])

        print("Length After", len(dots_in_tiff[i][1]))
    # --------------------------------------------------------

    return dots_in_tiff


def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic):
    # Getting Background Src
    # --------------------------------------------------------------------
    if bool_background_subtraction == True:
        background = get_background(tiff_src)
    # --------------------------------------------------------------------

    # Reading Tiff File
    # --------------------------------------------------------------------
    tiff = tiffy.load(tiff_src)
    # --------------------------------------------------------------------

    # Set Basic Variables
    # ---------------------------------------------------------------------
    dots_in_tiff = []

    tiff_shape = tiff.shape
    # ---------------------------------------------------------------------

    print("        Running on Channel:", end=" ", flush=True)

    # Loops through channels for Dot Detection
    # ---------------------------------------------------------------------
    if channels_to_detect_dots == 'all':

        channels = range(tiff.shape[1] - 1)
    else:
        channels = [int(channel) - 1 for channel in channels_to_detect_dots]

    for channel in channels:

        dots_in_channel = None

        tiff_3d = tiff[:, channel, :, :]

        if bool_background_subtraction == True:
            tiff_3d = run_back_sub(background, tiff_3d, channel, offset)

        print((channel + 1), end=" ", flush=True)

        dot_analysis = list(find_dots_3d(tiff_3d))

        assert len(dot_analysis[1]) > 0
        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)

        # Visualize Dots
        # ---------------------------------------------------------------------
        median_z = tiff.shape[0] // 2
        if bool_visualize_dots == True and channel == 1 and z == median_z:
            get_visuals(tiff_src, dot_analysis, tiff_2d)
        # ---------------------------------------------------------------------

        # Add dots to main dots in tiff
        # ---------------------------------------------------------------------
        dots_in_tiff.append(dot_analysis)
        print(f'{len(dots_in_tiff)=}')
        # ---------------------------------------------------------------------

    # -----------------------------------------------------------------

    threshed_dots_in_tiff = run_inflect_all_channels(dots_in_tiff)
    # print(f'{inflect_threshs=}')

    print("")
    return threshed_dots_in_tiff
