# from __future__ import annotations
import json
import os
import shutil
import tempfile
import warnings
from typing import Tuple

import cv2
import h5py
import numpy as np
import scipy.ndimage
from cv2 import createCLAHE
from skimage.feature import blob_log

from datapipeline.dot_detection.helpers.shift_locations import shift_locations
from datapipeline.load_tiff import tiffy

warnings.filterwarnings("ignore")


def find_dots_3d(chan_img, orig_img, min_sigma=2, max_sigma=2, sigma_std=1, overlap=.2) -> Tuple[
    np.ndarray, np.ndarray, int]:
    # Run LoG dot finder
    log_result = blob_log(
        chan_img,
        min_sigma=min_sigma,
        max_sigma=max_sigma,
        num_sigma=sigma_std,
        threshold=0,
        overlap=overlap
    )

    points = log_result[:, :3].astype(np.int64)
    intensities = orig_img.transpose()[points[:, 2], points[:, 1], points[:, 0]]

    return points, intensities  # , suggested_threshold


def run_image_processing(tiff_3d):
    # Correct 3d image
    # -----------------------------------------------
    correct_me = createCLAHE(clipLimit=4, tileGridSize=(1, 1))
    for z in range(tiff_3d.shape[0]):
        np.save('foo.npy', tiff_3d[z])

        tiff_3d[z] = correct_me.apply(tiff_3d[z])
    # -----------------------------------------------

    # Normalize 3d image
    # -----------------------------------------------
    minimum = 0
    maximum = 2000
    tiff_3d = (cv2.normalize(tiff_3d, None, minimum, maximum, norm_type=cv2.NORM_MINMAX))
    # -----------------------------------------------

    # Tophat 3d image
    # -----------------------------------------------
    for i in range(tiff_3d.shape[0]):
        kernel = np.full((50, 50), .1)
        tiff_3d[i] = cv2.morphologyEx(tiff_3d[i], cv2.MORPH_TOPHAT, kernel)
    # -----------------------------------------------

    return tiff_3d


def add_offset_to_locations(locations, offset, tiff_src, bool_chromatic):
    if np.all(offset == [0, 0, 0]):

        # No Shifting :(

        pass

    else:

        offset = np.array(offset)

        if bool_chromatic == True:

            split_tiff_src = tiff_src.split(os.sep)

            personal = split_tiff_src[4]

            experiment_name = split_tiff_src[6]

            chromatic_offsets_src = os.path.join('/groups/CaiLab/analyses', personal, experiment_name, \
                                                 analysis_name,
                                                 'Chromatic_Aberration_Correction/chromatic_offsets.json')

            with open(chromatic_offsets_src) as json_file:
                chromatic_offsets = np.array(json.load(json_file))

            # ---------------------------------------------------------------------

            # Shift for chromatic aberration
            # ---------------------------------------------------------------------
            key = "Channel " + str(channel)

            if chromatic_offsets[key] != [0, 0, 0]:
                offset = offset + chromatic_offset
            # ---------------------------------------------------------------------

        print("        Shifting locations for Alignment", flush=True)

        # Shifting Dot locations
        print('Shifting Dot Locations')

    locations_offsetted = [location + offset for location in locations]

    return locations_offsetted


def remove_out_of_place_locs(dot_analysis, upper_bound=2048, lower_bound=0, debug=False):
    len_locs = len(dot_analysis[0])

    i = 0
    out_of_place = []
    while i < len_locs:
        if (dot_analysis[0][i] < upper_bound).all() and (dot_analysis[0][i] > lower_bound).all():
            # print('Keeping', locations_offsetted[i])
            i += 1
            pass
        else:
            print('OUt of boudns deletion')
            out_of_place.append(dot_analysis[0][i])

            dot_analysis[0] = np.delete(dot_analysis[0], i, axis=0)
            dot_analysis[1] = np.delete(dot_analysis[1], i)

            i -= 1
            len_locs = len(locations_offsetted)
            # print(f'{i=}')

    if debug == True:
        return dot_analysis, out_of_place

    if debug == False:
        return dot_analysis


def get_dots_for_tiff(tiff_src, offset, analysis_name, bool_visualize_dots, bool_normalization, \
                      bool_background_subtraction, channels_to_detect_dots, bool_chromatic):
    # Getting Background Src
    # --------------------------------------------------------------------
    if bool_background_subtraction == True:
        tiff_split = tiff_src.split(os.sep)
        tiff_split[-2] = 'background'
        background_src = (os.sep).join(tiff_split)

        background = tiffy.load(background_src)
        background = background[:, [0, 2, 1, 3], :, :]
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

    # Print RUnning Chromatic aberration
    # ---------------------------------------------------------------------
    if bool_chromatic == True:
        print("        Shifting image for Chromatic aberration", flush=True)
    # ---------------------------------------------------------------------

    print("        Running on Channel:", end=" ", flush=True)

    # Loops through channels for Dot Detection
    # ---------------------------------------------------------------------
    if channels_to_detect_dots == 'all':

        channels = range(tiff.shape[1] - 1)
    else:
        channels = [int(channel) - 1 for channel in channels_to_detect_dots]
    # ---------------------------------------------------------------------

    # Declare tmp directory
    # ---------------------------------------------------------------------
    input_dir = tempfile.TemporaryDirectory()
    temp_file_h5s = []
    print(f'{input_dir.name=}')
    # ---------------------------------------------------------------------

    for channel in channels:

        tiff_3d = tiff[:, channel, :, :]

        # print((channel+1), end = " ", flush =True)

        dots_in_channel = None

        # Loops through Z-stacks to create temporary tiff files
        # ---------------------------------------------------------------------
        for z in range(tiff.shape[0]):

            if bool_background_subtraction == True:
                background3d = scipy.ndimage.interpolation.shift(background[:, channel, :, :], np.negative(offset))

                background_2d = background3d[0, :, :]

                tiff_3d[z, :, :] = cv2.subtract(tiff_3d[z, :, :], background_2d)
                tiff_3d[z, :, :][tiff_3d[z, :, :] < 0] = 0

        # Run image processing
        # ---------------------------------------------------------------------
        tiff_3d_processed = run_image_processing(tiff_3d)
        # ---------------------------------------------------------------------

        # Create Temp file
        # ---------------------------------------------------------------------
        file_name = "Ch" + str(channel) + '.h5'

        temp_file_h5 = os.path.join(input_dir.name, file_name)

        temp_file_h5s.append(temp_file_h5)

        h5_dest = os.path.join(input_dir.name, file_name)
        hf = h5py.File(h5_dest, 'w')
        hf.create_dataset('img_3d', data=tiff_3d_processed, chunks=True)
        hf.close()
        # ---------------------------------------------------------------------
    # ---------------------------------------------------------------------

    # Run ilastik probabilities
    # ---------------------------------------------------------------------
    print("Contents of tmpdir", os.listdir(input_dir.name))

    temp_dir_for_probs = tempfile.TemporaryDirectory()

    temp_file_for_probs = os.path.join(temp_dir_for_probs.name, '{nickname}.npy')

    cmd = '/groups/CaiLab/personal/nrezaee/ilastik/ilastik-1.3.3post3-Linux/run_ilastik.sh --headless --project=/groups/CaiLab/personal/nrezaee/ilastik/projects/intron_trained_with_3d_4_more_processing.ilp --export_source="Probabilities" --output_format=numpy --output_filename_format={} '

    cmd = cmd.format(temp_file_for_probs)

    for temp_file_h5 in temp_file_h5s:
        cmd = cmd + ' ' + temp_file_h5

    # print(f'{cmd=}')

    os.system(cmd)

    prob_files = os.listdir(temp_dir_for_probs.name)

    # print('Contents of returned tempdir', prob_files)
    # ---------------------------------------------------------------------

    # Run Dot detection on probabilities
    # ---------------------------------------------------------------------
    for channel in channels:
        channel_result_file_path = os.path.join(temp_dir_for_probs.name, 'Ch' + str(channel) + '.npy')

        channel_result = np.load(channel_result_file_path)[:, :, :, 0]

        # channel_result = np.where(channel_result < .99, 0, channel_result)

        orig_file_path = os.path.join(input_dir.name, 'Ch' + str(channel) + '.h5')

        orig_img = h5py.File(orig_file_path, 'r')['img_3d'].value

        # Get dots from 3d image
        # ---------------------------------------------------------------------
        dot_analysis = list(find_dots_3d(channel_result, orig_img, min_sigma=1.5, max_sigma=2, sigma_std=1, overlap=.5))
        # ---------------------------------------------------------------------

        # Switch [z, y, x] to [x, y, z]
        # ---------------------------------------------------------------------
        dot_analysis[0][:, [0, 1, 2]] = dot_analysis[0][:, [2, 1, 0]]
        # ---------------------------------------------------------------------

        dot_analysis[0] = shift_locations(dot_analysis[0], np.array(offset), tiff_src, bool_chromatic)

        print(f'{len(dot_analysis[1])=}', flush=True)
        # Add dots to main dots in tiff
        # ---------------------------------------------------------------------
        dots_in_tiff.append(dot_analysis)
        # ---------------------------------------------------------------------

    # -----------------------------------------------------------------

    print("")

    shutil.rmtree(temp_dir_for_probs.name)
    shutil.rmtree(input_dir.name)

    return dots_in_tiff
