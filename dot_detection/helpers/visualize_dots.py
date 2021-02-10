import cv2
import numpy as np
import os
import tifffile
import imageio
import matplotlib.pyplot as plt

def plot_and_save_locations(img_array, locations_2d, dest):
    
    plt.figure(figsize=(40,40))
    plt.imshow(img_array*17, cmap='gray')
    print(f'{locations_2d.shape=}')
    print(f'{locations_2d[:10]=}')
    plt.scatter(locations_2d[:,0], locations_2d[:,1], s= 2, c='r')
    plt.savefig(dest)
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
        os.mkdir(visualize_dots_dir)
    
    dest = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots', hyb + 'test.png')
    
    #dest = os.path.join('/home/nrezaee/sandbox/', 'channel_' + str(channel) + '_Z_' + str(z) + '.tiff')
    
    plot_and_save_locations(tiff_2d, dot_analysis[0], dest)