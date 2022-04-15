from __future__ import annotations

import cv2
import numpy as np
import tifffile


def plot_and_save_locations(img_array, locations_2d, dest):
    # Convert from grayscale to RGB
    # -------------------------------------------------------------------------
    img_array_rgb = cv2.cvtColor(np.float32(img_array), cv2.COLOR_GRAY2RGB)
    # -------------------------------------------------------------------------

    # Plot the locations on the image
    # -------------------------------------------------------------------------
    for location in locations_2d:
        img_array_rgb = cv2.circle(img_array_rgb, (location[0], location[1]), radius=2, color=(255, 0, 0), thickness=-1)
    # -------------------------------------------------------------------------

    # Write results to tiff file
    # -------------------------------------------------------------------------
    tifffile.imwrite(dest, img_array_rgb.astype(np.float16))
    # -------------------------------------------------------------------------

    return None
