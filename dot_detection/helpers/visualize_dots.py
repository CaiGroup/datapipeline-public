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
    
def save_plotted_locs(img_2d, df_locs, dest):
    plt.figure(figsize=(20,20))
    plt.imshow(img_2d*17)
    plt.scatter(df_locs.x, df_locs.y, color='r', s= 2)
    plt.savefig(dest)
    

def get_visuals(tiff_src, df_locs_2d, tiff_2d, analysis_name):

    tiff_split = tiff_src.split(os.sep)
    
    personal = tiff_split[4]
    
    exp_name = tiff_split[6]
    
    hyb = tiff_split[7]
    
    position = tiff_split[8].split('.ome')[0]
    
    visualize_dots_dir = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots')
                        
    if not os.path.exists(visualize_dots_dir):
        try:
            os.mkdir(visualize_dots_dir)
        except:
            pass
    
    dest = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots', hyb + 'test.png')
    
    #dest = os.path.join('/home/nrezaee/sandbox/', 'channel_' + str(channel) + '_Z_' + str(z) + '.tiff')
    
    save_plotted_locs(tiff_2d, df_locs_2d, dest)
    
    
    
    
def plot_and_save_locations_3d(img_array, locations, dest,z):
    
    plt.figure(figsize=(40,40))
    plt.imshow(np.log(img_array), cmap='gray')
    locations_2d = locations[((locations[:,2] - 1) < z) & ((locations[:,2] + 1) > z)]
    plt.scatter(np.array(locations_2d[:,0] - .5), np.array(locations_2d[:,1]) -.5 , facecolors='none', edgecolors='y', s=20, alpha=.35)
    print(f'{dest=}')
    plt.savefig(dest)
    return None
    
def plot_and_save_locations_3d_michal(img_array, locations_2d, dest):
    
    plt.figure(figsize=(40,40))
    plt.imshow(np.log(img_array), cmap='gray')
    plt.scatter(np.array(locations_2d[:,0] - .5), np.array(locations_2d[:,1]) -.5 , facecolors='none', edgecolors='y', s=20, alpha=.35)
    print(f'{dest=}')
    plt.savefig(dest)
    return None

def get_visuals_3d(tiff_src, dot_analysis, tiff_2d, analysis_name, z):

    # Set Path for results
    tiff_split = tiff_src.split(os.sep)
    personal = tiff_split[4]
    exp_name = tiff_split[6]
    hyb = tiff_split[7]
    position = tiff_split[8].split('.ome')[0]
    visualize_dots_dir = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots')
                        
    # Multiprocessing may through an error if this is not set
    if not os.path.exists(visualize_dots_dir):
        try:
            os.mkdir(visualize_dots_dir)
        except:
            pass
        
    
    # Save plot to png file
    dest = os.path.join('/groups/CaiLab/analyses', personal, exp_name, \
                        analysis_name, position, 'Visualize_Dots', hyb + '_visual.png')
    # if 'michal' in tiff_src:
    #     plot_and_save_locations_3d_michal(tiff_2d, dot_analysis[0], dest)
    # else:
    plot_and_save_locations_3d(tiff_2d, dot_analysis[0], dest, z)
    
    
    