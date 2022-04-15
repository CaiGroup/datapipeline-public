from __future__ import annotations

import warnings
from typing import Tuple

import cv2
import numpy as np
import scipy.ndimage as ndi
from scipy import ndimage
from scipy.ndimage._ni_support import _normalize_sequence
from skimage.feature import blob_log


def find_dots(chan_img: np.ndimage) -> Tuple[np.ndarray, np.ndarray, int]:
    """Find the locations and intensities of dots in an image channel.

    Subtracts background using a rolling ball filter, and then uses the
    Laplacian of Gaussian (LoG) method of blob detection provided by skimage.

    Args:
        img: 2-dimensional uint16 image.

    Returns:
        3-element tuple containing:
        - **points**: [N x 2] array of dot coordinates.
        - **intensities**: [N x 1] array of dot intensities.
        - **threshold**: Suggested minimum dot intensity threshold.
    """

    # Corresponds to a dot radius of sqrt(2)
    sigma = 2

    # Background subtraction with rolling ball radius of 3
    subtracted = rolling_ball_filter(chan_img, 3, spacing=None, top=False)

    # Scaled Laplacian over which blob_log maximizes to find dots
    laplacian = -ndimage.gaussian_laplace(subtracted, sigma) * sigma ** 2
    positive_laplacian = laplacian[laplacian > 0]

    # Mean of positive Laplacian values plus half of standard deviation has been
    # observed to be a good base threshold for capturing dots
    mean = np.mean(positive_laplacian)
    stdev = np.std(positive_laplacian)
    capture_threshold = np.round(mean + stdev / 2)

    # Run LoG dot finder
    log_result = blob_log(
        subtracted,
        min_sigma=sigma,
        max_sigma=sigma,
        num_sigma=1,
        threshold=capture_threshold,
    )

    points = log_result[:, :2].astype(np.int64)
    intensities = chan_img.transpose()[points[:, 1], points[:, 0]]

    # Suggest dots brighter than 15th percentile of dot intensities
    # suggested_threshold = int(np.percentile(intensities, 15))

    return points, intensities  # , suggested_threshold


def find_dots_faster(chan_img: np.ndimage) -> Tuple[np.ndarray, np.ndarray, int]:
    """Find the locations and intensities of dots in an image channel.

    Subtracts background using a rolling ball filter, and then uses the
    Laplacian of Gaussian (LoG) method of blob detection provided by skimage.

    Args:
        img: 2-dimensional uint16 image.

    Returns:
        3-element tuple containing:
        - **points**: [N x 2] array of dot coordinates.
        - **intensities**: [N x 1] array of dot intensities.
        - **threshold**: Suggested minimum dot intensity threshold.
    """

    # Corresponds to a dot radius of sqrt(2)
    sigma = 2

    # Background subtraction with rolling ball radius of 3
    # subtracted = rolling_ball_filter(chan_img, 3, spacing=None, top=False)

    # Scaled Laplacian over which blob_log maximizes to find dots
    laplacian = -ndimage.gaussian_laplace(chan_img, sigma) * sigma ** 2
    positive_laplacian = laplacian[laplacian > 0]

    # Mean of positive Laplacian values plus half of standard deviation has been
    # observed to be a good base threshold for capturing dots
    mean = np.mean(positive_laplacian)
    stdev = np.std(positive_laplacian)
    capture_threshold = np.round(mean + stdev / 2)

    # Run LoG dot finder
    log_result = blob_log(
        chan_img,
        min_sigma=sigma,
        max_sigma=sigma,
        num_sigma=1,
        threshold=capture_threshold,
    )

    points = log_result[:, :2].astype(np.int64)
    intensities = chan_img.transpose()[points[:, 1], points[:, 0]]

    # Suggest dots brighter than 15th percentile of dot intensities
    # suggested_threshold = int(np.percentile(intensities, 15))

    return points, intensities


def rolling_ball_filter(
        data: np.ndarray,
        ball_radius: float,
        spacing: Optional[Union[int, Sequence]] = None,
        top: bool = False,
) -> np.ndarray:
    """Rolling ball filter implemented with morphology operations.

    This implemetation is very similar to that in ImageJ and uses a top hat
    transform with a ball shaped structuring element with Image smoothing. Output
    is almost exactly as in ImageJ.

    Args:
        data: Image data (assumed to be on a regular grid).
        ball_radius: The radius of the ball to roll.
        spacing: The spacing of the image data.
        top: Whether to roll the ball on the top or bottom of the data.

    Returns:
        Data with background subtracted.
    """
    ndim = data.ndim
    if spacing is None:
        spacing = np.ones(ndim)
    else:
        spacing = _normalize_sequence(spacing, ndim)

    kernel = np.ones((3, 3), np.float64) / (3 * 3)
    _data = cv2.filter2D(data, -1, kernel)

    radius = np.asarray(_normalize_sequence(ball_radius, ndim))
    mesh = np.array(
        np.meshgrid(
            *[np.arange(-r, r + s, s) for r, s in zip(radius, spacing)],  # type: ignore
            indexing="ij"
        )
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        structure = 2 * np.sqrt(
            1 - ((mesh / radius.reshape(-1, *((1,) * ndim))) ** 2).sum(0)
        )
    structure[~np.isfinite(structure)] = 0
    if not top:
        # ndi.white_tophat(y, structure=structure, output=background)
        background = ndi.grey_erosion(_data, structure=structure)
        background = ndi.grey_dilation(background, structure=structure)
    else:
        # ndi.black_tophat(y, structure=structure, output=background)
        background = ndi.grey_dilation(_data, structure=structure)
        background = ndi.grey_erosion(background, structure=structure)

    data = data.astype("float64") - background.astype("float64")
    b = data < 0
    data[b] = 0

    return data
