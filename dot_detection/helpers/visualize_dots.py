import cv2
import numpy as np
import os
import tifffile
import imageio

def plot_and_save_locations(img_array, locations_2d, dest):
    
    #Convert from grayscale to RGB
    #-------------------------------------------------------------------------
    img_array_rgb = cv2.cvtColor(np.float32(img_array), cv2.COLOR_GRAY2RGB)
    #-------------------------------------------------------------------------
    
    print(f'{img_array.shape[0]//600=}')
    #Plot the locations on the image
    #-------------------------------------------------------------------------
    for location in locations_2d:
        img_array_rgb = cv2.circle(img_array_rgb, (location[0], location[1]), radius=2, color=(0, 255, 255), thickness=-1)
    #-------------------------------------------------------------------------
    
    
    #Write results to tiff file
    #-------------------------------------------------------------------------
    imageio.imwrite(dest, img_array_rgb)
    #-------------------------------------------------------------------------

    return None
    

def get_visuals(tiff_src, dot_analysis, tiff_2d, analysis_name):

    tiff_split = tiff_src.split(os.sep)
    
    personal = tiff_split[4]
    
    exp_name = tiff_split[6]
    
    hyb = tiff_split[7]
    
    position = tiff_split[8].split('.ome')[0]
    
    visualize_dots_dir = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots')
                        
    if not os.path.exists(visualize_dots_dir):
        os.makedirs(visualize_dots_dir)
    
    dest = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots', hyb + 'test.png')
    
    #dest = os.path.join('/home/nrezaee/sandbox/', 'channel_' + str(channel) + '_Z_' + str(z) + '.tiff')
    
    plot_and_save_locations(tiff_2d, dot_analysis[0], dest)