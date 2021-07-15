import matplotlib.pyplot as plt
import numpy as np
import glob
import sys
import os

sys.path.insert(0, '/home/nrezaee/test_cronjob_multi_dot')
from load_tiff import tiffy


def get_plots_of_tiff_check(tiff_src, dest = None):

    #Read in tiff file
    #--------------------------------------------
    tiff = tiffy.load(tiff_src, dest)
    print(f'{tiff.shape=}')
    #--------------------------------------------
    
    #Plot subplots of tiff
    #--------------------------------------------
    fig, axs = plt.subplots(tiff.shape[1], tiff.shape[0], figsize=(15,15))
    for ch in range(tiff.shape[1]):
        for z in range(tiff.shape[0]):
            #axs[ch, z].set_title('Channel ' + str(ch) + ' Z ' + str(z))
            if tiff.shape[0] > 1:
                axs[ch, z].imshow(np.log(tiff[z, ch]), cmap='gray')
            else:
                axs[ch].imshow(np.log(tiff[z, ch]), cmap='gray')
    #--------------------------------------------
    
    #Label Rows and columns
    #--------------------------------------------
    if tiff.shape[0] > 1:
        rows = ['Channel {}'.format(col) for col in range(1, tiff.shape[1] + 1)]
        cols = ['Z {}'.format(row) for row in range(1, tiff.shape[0] + 1)]
        
        for ax, col in zip(axs[0], cols):
            ax.set_title(col)
        
        for ax, row in zip(axs[:,0], rows):
            ax.set_ylabel(row, rotation=0, size='large')
    #--------------------------------------------
        
    if dest != None:
        #Save subplots
        #--------------------------------------------
        fig.savefig(dest)
        print(f'{dest=}')
        #--------------------------------------------
    
    
def get_opening_tiff_check(data_dir, position, dest):
    
    #Make directory that dest is in
    #--------------------------------------------
    os.makedirs(os.path.dirname(dest), exist_ok = True)
    #--------------------------------------------
    
    #Get Tiff File for check
    #--------------------------------------------
    glob_me_for_tiff_files = os.path.join(data_dir, 'HybCycle_*', position)
    print(f'{glob_me_for_tiff_files=}')
    tiff_files_for_pos = glob.glob(glob_me_for_tiff_files)
    
    assert len(tiff_files_for_pos) > 0, 'There are no tiff files found.'
    
    tiff_for_check_src = tiff_files_for_pos[0]
    #--------------------------------------------
    
    #Get Plots for tiff check
    #--------------------------------------------
    get_plots_of_tiff_check(tiff_for_check_src, dest)
    #--------------------------------------------
    
    
if sys.argv[1] == 'debug_plot_from_tiff_src':
    tiff_src = '/groups/CaiLab/personal/jina/raw/2021-06-11-USCKidney_35MaleR86_pseudo_4_shifted/HybCycle_16/MMStack_Pos15.ome.tif'
    dest = 'foo2.png'
    
    get_plots_of_tiff_check(tiff_src, dest)

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