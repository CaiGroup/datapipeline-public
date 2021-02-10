import cv2
import os
from load_tiff import tiffy

def apply_background_subtraction(background, tiff_2d, z, channel):
    background_2d = background[z, channel,:,:]
    tiff_2d = cv2.subtract(tiff_2d, background_2d)
    
    print("Running Background Subtraction")

    return tiff_2d

def get_background(tiff_src):
    tiff_split = tiff_src.split(os.sep)
    tiff_split[-2] = 'background'
    background_src = (os.sep).join(tiff_split)
    
    

    return background_src