import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.feature import blob_log

from ...load_tiff import tiffy


def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel = tuple(np.array(tiff_2d.shape) // num_tiles)
    blurry_img = cv2.blur(tiff_2d, blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)

    return tiff_2d


def blur_back_subtract_3d(img_3d, num_tiles=100):
    for i in range(img_3d.shape[0]):
        img_3d[i, :, :] = blur_back_subtract(img_3d[i, :, :], num_tiles)
    return img_3d


def normalize(img, max_norm=1000):
    norm_image = cv2.normalize(img, None, alpha=0, beta=max_norm, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return norm_image


def tophat_2d(img_2d):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)) * 4
    tophat_img = cv2.morphologyEx(img_2d, cv2.MORPH_TOPHAT, kernel)
    return tophat_img


def tophat_3d(img_3d):
    print(f'{img_3d.shape=}')
    for i in range(len(img_3d)):
        print(f'{i=}')
        img_3d[i] = tophat_2d(img_3d[i])
    return img_3d


def preprocess_img(img_3d):
    norm_img_3d = normalize(img_3d)
    blur_img_3d = blur_back_subtract_3d(norm_img_3d)
    print(f'{blur_img_3d.shape=}')
    # tophat_img_3d = tophat_3d(blur_img_3d)
    nonzero_img_3d = np.where(blur_img_3d < 0, 0, blur_img_3d)
    return nonzero_img_3d


def get_hist(intense, strictness):
    num_bins = 100
    plt.figure()
    print(f'{len(intense)=}')
    bins = np.arange(np.min(intense), np.max(intense), (np.max(intense) - np.min(intense)) / num_bins)
    y, x, ignore = plt.hist(intense, bins=bins, cumulative=-1)
    thresh = match_thresh_to_diff_stricter(y, x, strictness)
    plt.axvline(x=thresh, color='r')

    # if 'fid' not in hist_png_path:
    #     plt.savefig(hist_png_path)
    return y, x, thresh


def match_thresh_to_diff_stricter(y_hist, x_hist, strictness=1):
    hist_diffs = get_diff_in_hist(y_hist)
    index_of_max_diff = hist_diffs.index(max(hist_diffs)) + strictness

    print(f'{index_of_max_diff=}')
    thresh = x_hist[index_of_max_diff]

    return thresh


def get_diff_in_hist(y_hist):
    hist_diffs = []
    for i in range(len(y_hist) - 1):
        diff = y_hist[i] - y_hist[i + 1]
        hist_diffs.append(diff)

    return hist_diffs


def apply_thresh(dot_analysis, threshold):
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    for i in range(len(dot_analysis[1])):
        if dot_analysis[1][i] <= threshold:
            indexes.append(i)
    dot_analysis[0] = np.delete(dot_analysis[0], indexes, axis=0)
    dot_analysis[1] = np.delete(dot_analysis[1], indexes)
    print(f'{len(indexes)=}')
    return dot_analysis


def apply_reverse_thresh(dot_analysis, threshold):
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    for i in range(len(dot_analysis[1])):
        if dot_analysis[1][i] >= threshold:
            indexes.append(i)
    dot_analysis[0] = np.delete(dot_analysis[0], indexes, axis=0)
    dot_analysis[1] = np.delete(dot_analysis[1], indexes)
    print(f'{len(indexes)=}')
    return dot_analysis


def remove_unneeded_intensities(intensities, per_remove):
    num_bins = 100
    plt.figure()

    print(f'{len(intensities)=}')
    bins = np.arange(np.min(intensities), np.max(intensities), (np.max(intensities) - np.min(intensities)) / num_bins)
    y, x, ignore = plt.hist(intensities, bins=bins, cumulative=-1)

    bools = y < len(intensities) * per_remove
    i = 0
    while bools[i] == False:
        i += 1
    intensities = np.array(intensities)

    threshed = intensities[intensities < x[i]]

    return threshed, x[i]


def hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, dot_radius):
    # tiff_3d = preprocess_img(tiff_3d)
    res = blob_log(tiff_3d, min_sigma=dot_radius, max_sigma=dot_radius, num_sigma=1, threshold=0.01)
    points = res[:, :3]

    intensities = []
    for i in range(len(points)):
        intensities.append(tiff_3d[int(points[i, 0]), int(points[i, 1]), int(points[i, 2])])

    tiff_split = tiff_src.split(os.sep)
    personal = tiff_split[4]
    exp_name = tiff_split[6]
    hyb = tiff_split[7]
    position = tiff_split[8].split('.ome')[0]

    dot_analysis = [points, intensities]
    intensities, reverse_threshold = remove_unneeded_intensities(intensities, per_remove=.01)
    y, x, thresh = get_hist(intensities, strictness)
    points_threshed, intensities_threshed = apply_thresh(list(dot_analysis), thresh)
    points_threshed, intensities_threshed = apply_reverse_thresh([points_threshed, intensities_threshed],
                                                                 reverse_threshold)
    return points_threshed, intensities_threshed


if __name__ == '__main__':

    import sys

    if sys.argv[1] == 'debug_jump_helper':
        print(f'{np.version.version=}')

        tiff_src = '/groups/CaiLab/personal/michalp/raw/michal_1/HybCycle_10/MMStack_Pos20.ome.tif'
        tiff_3d = tiffy.load(tiff_src, num_wav=3)[:, 0]
        strictness = 5
        analysis_name = 'michal_decoding_top'
        print(f'{tiff_3d.shape=}')
        dot_radius = 2
        dot_analysis = list(hist_jump_threshed_3d(tiff_3d, strictness, tiff_src, analysis_name, dot_radius))
        print(f'{dot_analysis[0].shape=}')
