from scipy.io import loadmat
import multiprocessing
from numpy.core.multiarray import ndarray
from skimage.draw import polygon
from skimage.measure import regionprops_table
import matplotlib.pyplot as plt
import sys

import numpy as np
import pandas as pd
from read_roi import read_roi_zip


def get_labeled_img(roi_src, num_z=30, upto_cell=1000000000000):
    roi = read_roi_zip(roi_src)
    while len(roi) > upto_cell:
        roi.popitem()
    # convert polygon vertices to labeled image for each cell
    # ---------------------------------------------------------------------
    label_img = np.zeros((2048, 2048, num_z), dtype=np.uint8)
    cell_id = 1

    # Create polygon from vertices
    # ---------------------------------------------------------------------
    for key in roi:
        # get x, y indices of polygon
        r = roi[key]['y']
        c = roi[key]['x']

        # make polygon
        rr, cc = polygon(r, c)
        label_img[rr, cc, :] = cell_id
        cell_id += 1
    # ---------------------------------------------------------------------

    return label_img


def get_dot_analysis_for_channel(locs_ch, labeled_img):
    
    # np.save('locs_ch_1000.npy', locs_ch)
    # np.save('labeled_img_1000.npy', labeled_img)
    print(f'{labeled_img.shape=}')
    points = locs_ch[0]
    intensities = locs_ch[1]
    if intensities.shape[0] != 1:
        intensities = intensities.reshape(1,-1)
    
    #Get Indexes for each Cell
    #---------------------------------------------
    keyList = np.unique(labeled_img)
    seg_dict = {key: [] for key in keyList} 
    for i in range(len(points)):
        x = int(points[i][0])
        y = int(points[i][1])
        z = int(points[i][2])
        #print(x,y,z)
        if x < labeled_img.shape[1] and x >= 0 and \
            y < labeled_img.shape[2] and y >= 0 and \
            z < labeled_img.shape[0] and z >= 0:
            seg_dict[labeled_img[z, x, y]].append(i)
    #---------------------------------------------
    

    #Get Dot Analysis for each cell
    #---------------------------------------------
    for key in seg_dict.keys():
                #print(f'{key=}')
        if len(seg_dict[key]) == 0:
            low_rand = labeled_img.shape[0] + 100
            high_rand = labeled_img.shape[1] + 10000
            fake_points = np.random.uniform(low=low_rand, high=high_rand, size=(2,3))
            fake_intensities = np.random.uniform(low=0, high=.1, size=(1,2))
            #print(f'{points.shape=}')
            #print(f'{intensities.shape=}')
            seg_dict[key] = [fake_points, fake_intensities]
        else:
            # print(f'{points=}')
            # print(f'{intensities=}')
            # print(f'{)
            # points[seg_dict[key][:,[0,2]] = points[seg_dict[key][:,[2,0]]
            # points[seg_dict[key][:,[0,1]] = points[seg_dict[key][:,[1,0]]
            seg_dict[key] = [points[seg_dict[key]], intensities[:,seg_dict[key]]]
    #---------------------------------------------a
    
    return seg_dict

# locs_ch = np.load('locs_ch.npy', allow_pickle =True)
# labeled_img = np.load('labeled_img.npy', allow_pickle =True)
# seg_dict = get_dot_analysis_for_channel(locs_ch, labeled_img)


def save_plotted_cell(labeled_img, seg_dict_channel, fig_dest):
    plt.figure(figsize=(30,30))
    plt.imshow(labeled_img[labeled_img.shape[0]//2,:,:])
    plt.xlim([0,labeled_img.shape[1]])
    plt.ylim([0,labeled_img.shape[2]])
    
    for i in range(len(seg_dict_channel)):#len(seg_dict_channel)):
        
        points = seg_dict_channel[i][0]
        print(f'{points.shape=}')
        print(f'{points[:2]=}')
        
        plt.scatter(points[:,1][:100], points[:,0][:100], s=10)
        print(f'{fig_dest=}')
        
    plt.savefig(fig_dest)
        

def get_points_from_csv(locs_csv_src):
    my_points = pd.read_csv(locs_csv_src)
    hybs = my_points.hyb.unique()
    print(f'{hybs=}')
    chs = my_points.ch.unique()
    print(f'{chs=}')

    locs = []
    for hyb in hybs:
        for ch in chs:
            locs_ch = my_points[(my_points.hyb == hyb) & (my_points.ch == ch)]
            # all_points.append(np.array(locs_ch[['x','y','z']]))
            # all_intensities.append(np.array(locs_ch[['int']]))
            locs.append([ np.array(locs_ch[['x','y','z']]), np.array(locs_ch[['int']])])
            
    return locs
    
def get_segmentation_dict_dots(locations_src, labeled_img, fig_dest):

    locs = get_points_from_csv(locations_src)

    #Get Segmented Dictionary
    #----------------------------------------------
    all_seg_dict = {}
    check_if_first_channel = 0
    i = 0
    #Go through Each Channel
    for locs_ch in locs:
        print(f'{i=}')

        seg_dict_channel = get_dot_analysis_for_channel(locs_ch, labeled_img)
        #print(f'{np.unique(labeled_img)=}')
        print(f'{len(seg_dict_channel[0])=}')
        if i == 1:
            print('Plotting')
            #fig_dest = 'plotted_cells.png'
            save_plotted_cell(labeled_img, seg_dict_channel, fig_dest)
            
            
     
        if check_if_first_channel == 0:
            all_seg_dict = seg_dict_channel
            for key in list(all_seg_dict.keys()):
                all_seg_dict[key][0] = [all_seg_dict[key][0], all_seg_dict[key][1]]
                all_seg_dict[key].pop(1)
     
            check_if_first_channel += 1   
        else:
            #key = 0
            for key in list(all_seg_dict.keys()):
                all_seg_dict[key].append(seg_dict_channel[key])
        i+=1
    #----------------------------------------------
    
    return all_seg_dict


if sys.argv[1] == 'debug_seg_dict':    
    roi_src = '/groups/CaiLab/personal/nrezaee/raw/intron_pos0/segmentation/RoiSet.zip'
    labeled_img  = get_labeled_img(roi_src)
    
    locations_src = '/groups/CaiLab/analyses/nrezaee/test1-big/cellpose/MMStack_Pos0/Dot_Locations/locations.csv'
    fig_dst = '/tmp/fig.png'
    seg_dict = get_segmentation_dict_dots(locations_src, labeled_img, fig_dst)
