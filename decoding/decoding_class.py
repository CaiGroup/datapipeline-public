import os
import json
import sys
import numpy as np
import glob
import pandas as pd
import tifffile
import shutil

sys.path.insert(0, os.getcwd())
from helpers.reorder_hybs import get_and_sort_hybs
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose

#Barcode Script
#----------------------------
from read_barcode import read_barcode
#----------------------------


#Decoding Script
#----------------------------
from decoding import lampfish, lampfish_ch2
from decoding.lampfish_helpers import lampfish_analytics
from decoding import decoding_non_parallel
from decoding import decoding_parallel
from decoding import previous_points_decoding as previous_points_decoding
from decoding import previous_locations_decoding as previous_locations_decoding
from decoding import decoding_non_barcoded
from decoding import syndrome_decoding
#----------------------------

#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Decoding:
    def __init__(self, data_dir, position, decoded_dir, locations_dir, position_dir, barcode_dst, barcode_src, \
                    bool_decoding_with_previous_dots, bool_decoding_with_previous_locations, \
                    bool_fake_barcodes, bool_decoding_individual, min_seeds, allowed_diff, dimensions, \
                    num_zslices, segmentation, decode_only_cells, labeled_img, num_wav, synd_decoding, \
                    lampfish_pixel, start_time):
        
        self.data_dir = data_dir
        self.position = position
        self.locations_dir = locations_dir        
        self.position_dir = position_dir
        self.decoded_dir = decoded_dir
        self.barcode_dst = barcode_dst
        self.barcode_src = barcode_src
        self.decoding_with_previous_dots = bool_decoding_with_previous_dots
        self.decoding_with_previous_locations = bool_decoding_with_previous_locations
        self.fake_barcodes = bool_fake_barcodes 
        self.decoding_individual = bool_decoding_individual
        self.min_seeds = min_seeds
        self.allowed_diff = allowed_diff
        self.dimensions = dimensions
        self.num_zslices = num_zslices
        self.seg = segmentation
        self.decode_only_cells = decode_only_cells
        self.labeled_img = labeled_img
        self.num_wav = num_wav
        self.synd_decoding = synd_decoding
        self.lampfish_pixel = lampfish_pixel
        self.start_time = start_time
         
    def labeled_img_from_tiff_dir(self):
        glob_me = os.path.join(self.data_dir, '*')
        
        hybs = get_and_sort_hybs(glob_me)
        
        assert len(hybs) >= 1
        
        tiff_for_seg = os.path.join(hybs[0], self.position)
        print(f'{tiff_for_seg=}')
        labeled_img = get_labeled_img_cellpose(tiff_for_seg)
    
        return labeled_img
            
    def combine_decode_z_s(self, decode_channel_dir):
        
        #Get Csv's
        #-----------------------------------------------------
        glob_me = os.path.join(decode_channel_dir, '*', 'pre_seg_diff*.csv')
        
        csv_s = glob.glob(glob_me)
        
        assert len(csv_s) > 0, "There are no csv's in the Z Slices for segmentation"
        #-----------------------------------------------------
        
        #Separate Filtered and unfiltered
        #-----------------------------------------------------
        filt_csv_s = [csv for csv in csv_s if '_filtered' in csv]
        unfilt_csv_s = [csv for csv in csv_s if 'unfiltered' in csv]
        print(f'{unfilt_csv_s=}')
        #-----------------------------------------------------
        
        #Concatenate Csv's
        #-----------------------------------------------------
        #Filtered
        #----------------------------------
        df_concat_filt = pd.read_csv(filt_csv_s[0])
        
        for i in range(1, len(filt_csv_s)):
            df_concat_me = pd.read_csv(filt_csv_s[i])
            
            df_concat_filt = pd.concat([df_concat_filt, df_concat_me])
        #----------------------------------
        
        #UnFiltered
        #----------------------------------
        df_concat_unfilt = pd.read_csv(unfilt_csv_s[0])
        print(f'{df_concat_unfilt.shape=}')
        for i in range(1, len(unfilt_csv_s)):
            df_concat_me = pd.read_csv(unfilt_csv_s[i])
            
            df_concat_unfilt = pd.concat([df_concat_unfilt, df_concat_me])
            print(f'{df_concat_unfilt.shape=}')
        #----------------------------------
        #-----------------------------------------------------
        
        
        #Save Concatenated Csv
        #-----------------------------------------------------
        #Filtered
        #----------------------------------
        dir_name, filt_file_name = os.path.split(filt_csv_s[0])
        filt_dst = os.path.join(decode_channel_dir, filt_file_name)
        df_concat_unfilt.to_csv(filt_dst, index=False)
        #----------------------------------
        
        #UnFiltered
        #----------------------------------
        dir_name, unfilt_file_name = os.path.split(unfilt_csv_s[0])
        unfilt_dst = os.path.join(decode_channel_dir, unfilt_file_name)
        df_concat_unfilt.to_csv(unfilt_dst, index=False)  
        #----------------------------------
        #-----------------------------------------------------
        
    def run_decoding_across(self):

        if self.dimensions == 2:
            self.run_decoding_across_2d()
            return None
            
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_src, 'barcode.csv')
        
                                  
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_file_path = os.path.join(self.barcode_dst, 'barcode.mat')
        #--------------------------------------------------------------------
        
        
        #Read the barcode to a mat file
        #--------------------------------------------------------------------
        read_barcode.read_barcode(barcode_src, barcode_file_path, self.fake_barcodes)
        #--------------------------------------------------------------------
        
        
        #Set Directory for locations
        #--------------------------------------------------------------------
        locations_path = os.path.join(self.locations_dir, 'locations.csv')
        #--------------------------------------------------------------------
        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        #Run Decoding Across Channels
        #--------------------------------------------------------------------
        print("Running Decoding Across Channels")
        
        if self.seg == False:
            
            decoding.decoding(barcode_file_path, locations_path, self.decoded_dir, allowed_diff = self.allowed_diff, min_seeds = self.min_seeds)
            
        else:
            
            print('Shape in Decoding Class: ' +  str(self.labeled_img.shape))
            decoding_parallel.decoding(barcode_file_path, locations_path, self.labeled_img, self.decoded_dir, self.allowed_diff, \
                    self.min_seeds, start_time, decode_only_cells = self.decode_only_cells)
                    
 
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
    def run_non_barcoded_decoding(self):
        barcode_src = os.path.join(self.data_dir, 'non_barcoded_genes', 'sequential_key.csv')
        
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_file_path = os.path.join(self.barcode_dst, 'sequential_key.csv')
        shutil.copyfile(barcode_src, barcode_file_path)
        
        #Set Directory for locations
        #--------------------------------------------------------------------
        locations_path = os.path.join(self.locations_dir, 'locations.csv')
        #--------------------------------------------------------------------
        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        print("Running Sequential Decoding (smFISH)")
        
        pos_num = int(self.position.split('.ome.tif')[0].split('Pos')[1])
        decoding_non_barcoded.run_decoding_non_barcoded(barcode_src, locations_path, pos_num, self.decoded_dir)
        
        
    def run_decoding_across_2d(self):
        
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_src, 'barcode.csv')
        
                                  
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_file_path = os.path.join(self.barcode_dst, 'barcode.mat')
        #--------------------------------------------------------------------
        
        
        #Read the barcode to a mat file
        #--------------------------------------------------------------------
        read_barcode.read_barcode(barcode_src, barcode_file_path, self.fake_barcodes)
        #--------------------------------------------------------------------
        
        
        #Set Directory for locations
        #--------------------------------------------------------------------
        locations_path = os.path.join(self.locations_dir, 'locations.csv')
        #--------------------------------------------------------------------
        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        #Get Labeled Img
        #--------------------------------------------------------------------
        # if self.seg != False:

        #     if self.seg == "roi":
        #         labeled_img = self.labeled_img_from_tiff_dir()
                    
        #--------------------------------------------------------------------
        
        for z in range(self.num_zslices):
        
            #Set file path for locations
            #--------------------------------------------------------------------
            locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
                        
            locations_file_name = 'locations_z_' + str(z) +'.csv'
            
            locations_path_z = os.path.join(locations_dir, locations_file_name)
            #--------------------------------------------------------------------
        
            
            #Set directories for decoding
            #--------------------------------------------------------------------
            if not os.path.exists(self.decoded_dir):
                os.makedirs(self.decoded_dir)
                
            decoding_dst_for_channel = self.decoded_dir

            
            z_dir = 'Z_Slice_' +str(z)
            
            decoding_dst_z = os.path.join(self.decoded_dir, z_dir)
                                  
            if not os.path.exists(decoding_dst_z):
                os.makedirs(decoding_dst_z)
            #--------------------------------------------------------------------
            
            #Run Decoding Across Channels
            #--------------------------------------------------------------------
            print("Running Decoding Across Channels")
            
            if self.seg == False:
                decoding.decoding(barcode_file_path, locations_path_z, decoding_dst_z, allowed_diff = self.allowed_diff, min_seeds = self.min_seeds)
            
            else:
                    
                decoding_parallel.decoding(barcode_file_path, locations_path_z, self.labeled_img, decoding_dst_z, self.allowed_diff,  \
                    self.min_seeds, decode_only_cells = self.decode_only_cells)
            print("Finished Decoding Across Channels")
            #--------------------------------------------------------------------
            
        self.combine_decode_z_s(self.decoded_dir)
        
    def run_decoding_individual_2d(self):

        #Loop through each individual channel
        #--------------------------------------------------------------------
        for channel in self.decoding_individual:
        
            #Set Directories for reading barcode key
            #--------------------------------------------------------------------
            barcode_file_name = 'channel_' + str(channel) + '.csv'
            
            barcode_src = os.path.join(self.barcode_src, barcode_file_name)
                                      
            if not os.path.exists(self.barcode_dst):
                os.makedirs(self.barcode_dst)
                
            barcode_file_mat = barcode_file_name.replace('.csv', '.mat')
                
            barcode_dst = os.path.join(self.barcode_dst, barcode_file_mat)
            #--------------------------------------------------------------------
        
            
            #Read barcode key into .mat file
            #--------------------------------------------------------------------
            read_barcode.read_barcode(barcode_src, barcode_dst, self.fake_barcodes)
            #--------------------------------------------------------------------
            
            for z in range(self.num_zslices):
            
                #Set file path for locations
                #--------------------------------------------------------------------
                locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
                            
                locations_file_name = 'locations_z_' + str(z) +'.csv'
                
                locations_path_z = os.path.join(locations_dir, locations_file_name)
                #--------------------------------------------------------------------
            
                
                #Set directories for decoding
                #--------------------------------------------------------------------
                if not os.path.exists(self.decoded_dir):
                    os.makedirs(self.decoded_dir)
                    
                decoding_dst_for_channel = os.path.join(self.decoded_dir, "Channel_"+str(channel))
                                      
                if not os.path.exists(decoding_dst_for_channel):
                    os.makedirs(decoding_dst_for_channel)
                    
                
                z_dir = 'Z_Slice_' +str(z)
                
                decoding_dst_for_channel_z = os.path.join(decoding_dst_for_channel, z_dir)
                                      
                if not os.path.exists(decoding_dst_for_channel_z):
                    os.makedirs(decoding_dst_for_channel_z)
                #--------------------------------------------------------------------
            
                if self.seg == False:
                    #Run decoding for individual channel
                    #--------------------------------------------------------------------
                    decoding.decoding(barcode_dst, locations_path_z, decoding_dst_for_channel_z, self.allowed_diff, self.min_seeds, self.decoding_individual.index(channel), \
                                      len(self.decoding_individual))
                    #--------------------------------------------------------------------
                else:
                    decoding_parallel.decoding(barcode_dst, locations_path_z, self.labeled_img, decoding_dst_for_channel_z, self.allowed_diff, self.min_seeds, \
                        self.decoding_individual.index(channel), len(self.decoding_individual), decode_only_cells = self.decode_only_cells)
                #--------------------------------------------------------------------
                
            self.combine_decode_z_s(decoding_dst_for_channel)

    def run_decoding_individual(self):
        
        print('In Decoding Individual')        
        if self.dimensions == 2:
            self.run_decoding_individual_2d()
            return None

        #Loop through each individual channel
        #--------------------------------------------------------------------
        for channel in self.decoding_individual:
            
            #Set Directories for reading barcode key
            #--------------------------------------------------------------------
            barcode_file_name = 'channel_' + str(channel) + '.csv'
            
            barcode_src = os.path.join(self.barcode_src, barcode_file_name)
            
            
     
            if not os.path.exists(self.barcode_dst):
                os.makedirs(self.barcode_dst)
                
            barcode_file_mat = barcode_file_name.replace('.csv', '.mat')
                
            barcode_dst = os.path.join(self.barcode_dst, barcode_file_mat)
            #--------------------------------------------------------------------
        
            
            #Read barcode key into .mat file
            #--------------------------------------------------------------------
            read_barcode.read_barcode(barcode_src, barcode_dst, self.fake_barcodes)
            #--------------------------------------------------------------------
        
            #Set file path for locations
            #--------------------------------------------------------------------
            locations_path = os.path.join(self.locations_dir, 'locations.csv')
            #--------------------------------------------------------------------
        
            
            #Set directories for decoding
            #--------------------------------------------------------------------
            if not os.path.exists(self.decoded_dir):
                os.makedirs(self.decoded_dir)
                
            decoding_dst_for_channel = os.path.join(self.decoded_dir, "Channel_"+str(channel))
                                  
            if not os.path.exists(decoding_dst_for_channel):
                os.makedirs(decoding_dst_for_channel)
            #--------------------------------------------------------------------
            
            if self.seg == False:
                #Run decoding for individual channel
                #--------------------------------------------------------------------
                decoding_non_parallel.decoding(barcode_dst, locations_path, decoding_dst_for_channel, self.allowed_diff, self.min_seeds, self.decoding_individual.index(channel), \
                                  len(self.decoding_individual))
                #--------------------------------------------------------------------
            else:
                
                #Run Decoding Across Channels
                #--------------------------------------------------------------------
                print('Shape in Decoding Class: ' +  str(self.labeled_img.shape))
                decoding_parallel.decoding(barcode_dst, locations_path, self.labeled_img, decoding_dst_for_channel, self.allowed_diff, self.min_seeds, \
                    self.decoding_individual.index(channel), len(self.decoding_individual), decode_only_cells = self.decode_only_cells)
                
            print("Finished Decoding Across Channels")
            #--------------------------------------------------------------------
            
    def run_decoding_with_previous_dots(self):
        
        
        #Get Previous Locations
        #--------------------------------------------------------------------
        glob_me = os.path.join(self.data_dir, 'points', '*.mat')
        
        mat_file_paths = glob.glob(glob_me)
        
        assert len(mat_file_paths) >0, "The points file is not in the right place."
        
        assert len(mat_file_paths) == 1, "There can only be one mat file in the points directory or \
                                         the pipeline cannot determine which mat file has the points."
                                         
        mat_file_path = mat_file_paths[0]
        #--------------------------------------------------------------------
        
        
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_src, 'barcode.csv')
                                  
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_dst = os.path.join(self.barcode_dst, 'barcode.mat')
        #--------------------------------------------------------------------
        
        
        #Read the barcode to a mat file
        #--------------------------------------------------------------------
        read_barcode.read_barcode(barcode_src, barcode_dst, self.fake_barcodes)
        #--------------------------------------------------------------------
        
        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        #Run Decoding Across Channels
        #--------------------------------------------------------------------
        print("Running Decoding Across Channels")
        
        previous_points_decoding.decoding(barcode_dst, mat_file_path, decoding_dst, self.allowed_diff, self.min_seeds)
        
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
    def run_decoding_with_previous_locations(self):
        
        #Get Previous Locations
        #--------------------------------------------------------------------
        glob_me = os.path.join(self.data_dir, 'locations', '*.mat')
        
        mat_file_paths = glob.glob(glob_me)
        print(f'{glob_me=}')
        
        assert len(mat_file_paths) == 1, "There can only be one mat file in the locations directory or \
                                         the pipeline cannot determine which mat file has the points."
                                         
        mat_file_path = mat_file_paths[0]
        #--------------------------------------------------------------------
        
        
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_src, 'barcode.csv')
                                  
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_dst = os.path.join(self.barcode_dst, 'barcode.mat')
        #--------------------------------------------------------------------
        
        
        #Read the barcode to a mat file
        #--------------------------------------------------------------------
        read_barcode.read_barcode(barcode_src, barcode_dst, self.fake_barcodes)
        #--------------------------------------------------------------------
        

        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
 
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        #Run Decoding Across Channels
        #--------------------------------------------------------------------
        print("Running Decoding Across Channels")
        
        previous_locations_decoding.decoding(barcode_dst, mat_file_path, self.decoded_dir, allowed_diff = self.allowed_diff, min_seeds = self.min_seeds)
        
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
    def run_synd_decoding_individual(self):
        
        #Loop through each individual channel
        #--------------------------------------------------------------------
        for channel in self.decoding_individual:
            
            #Set Directories for reading barcode key
            #--------------------------------------------------------------------
            barcode_file_name = 'channel_' + str(channel) + '.csv'
            barcode_src = os.path.join(self.barcode_src, barcode_file_name)
            #--------------------------------------------------------------------
        
            #Set file path for locations
            #--------------------------------------------------------------------
            locations_path = os.path.join(self.locations_dir, 'locations.csv')
            #--------------------------------------------------------------------
        
            
            #Set directories for decoding
            #--------------------------------------------------------------------
            if not os.path.exists(self.decoded_dir):
                os.makedirs(self.decoded_dir)
                
            decoding_dst_for_channel = os.path.join(self.decoded_dir, "Channel_"+str(channel))
            if not os.path.exists(decoding_dst_for_channel):
                os.makedirs(decoding_dst_for_channel)
            #--------------------------------------------------------------------
            
            #Run Syndrome Decoding
            #--------------------------------------------------------------------
            syndrome_decoding.run_syndrome_decoding(locations_path, barcode_src, decoding_dst_for_channel, self.fake_barcodes)
            #--------------------------------------------------------------------

    def run_lampfish_decoding(self):
        
        #Set file path for locations
        #--------------------------------------------------------------------
        locations_path = os.path.join(self.locations_dir, 'locations.csv')
        #--------------------------------------------------------------------
        
        #Set file path for offsets
        #--------------------------------------------------------------------
        offsets_path = os.path.join(self.position_dir, 'offsets.json')
        #--------------------------------------------------------------------

        #Set position and dst
        #--------------------------------------------------------------------
        os.makedirs(self.decoded_dir, exist_ok=True)
        pos = int(self.position.split('MMStack_Pos')[1].split('.ome.tif')[0])
        ratio_locs_dst = os.path.join(self.decoded_dir, 'lampfish_ratio_results.csv')
        #--------------------------------------------------------------------

        #Get Channel Offsets
        #--------------------------------------------------------------------
        channel_offsets_dst = os.path.join(self.decoded_dir, 'channel_offsets.json')
        lampfish.get_channel_offsets(self.data_dir, self.position, channel_offsets_dst, self.num_wav)
        #--------------------------------------------------------------------
        
        #Get first channel
        #--------------------------------------------------------------------
        lampfish.get_ratio_of_channels(offsets_path, channel_offsets_dst, locations_path, self.data_dir, pos, \
                                        ratio_locs_dst, self.num_wav, self.lampfish_pixel)
        #--------------------------------------------------------------------

        #Get Analytics
        #--------------------------------------------------------------------
        ratio_visual_dst = os.path.join(self.decoded_dir, 'lampfish_ratio_visual.png')
        lampfish_analytics.get_ratio_visualization(ratio_locs_dst, ratio_visual_dst)
        #--------------------------------------------------------------------

if sys.argv[1] == 'debug_decoding_class_synd':
    decoder = Decoding(data_dir = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei', 
                        position = 'MMStack_Pos0.ome.tif', 
                        decoded_dir = 'foo/test_decoding_class', 
                        locations_dir = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/Dot_Locations/', 
                        position_dir = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/', 
                        barcode_dst = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/BarcodeKey/', 
                        barcode_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/barcode_key', 
                        bool_decoding_with_previous_dots = False, 
                        bool_decoding_with_previous_locations = False, 
                        bool_fake_barcodes = True, 
                        bool_decoding_individual = [1], 
                        min_seeds = None, 
                        allowed_diff = None, 
                        dimensions = 3, 
                        num_zslices = None, 
                        segmentation = None, 
                        decode_only_cells = True, 
                        labeled_img = None, 
                        num_wav = 4, 
                        synd_decoding = True)
    print('Made Decoding Class')
    
    decoder.run_synd_decoding_individual()

elif sys.argv[1] == 'debug_decoding_class_lampfish_linus':
    decoder = Decoding(data_dir = '/groups/CaiLab/personal/Linus/raw/5ratiometric_test', 
                        position = 'MMStack_Pos0.ome.tif', 
                        decoded_dir = 'foo/test_decoding_class/lampfish', 
                        locations_dir = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/Dot_Locations/', 
                        position_dir = '/groups/CaiLab/analyses/Linus/5ratiometric_test/linus_5ratio_all_pos/MMStack_Pos0/', 
                        barcode_dst = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/BarcodeKey/', 
                        barcode_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/barcode_key', 
                        bool_decoding_with_previous_dots = False, 
                        bool_decoding_with_previous_locations = False, 
                        bool_fake_barcodes = False, 
                        bool_decoding_individual = 'all', 
                        min_seeds = None, 
                        allowed_diff = None, 
                        dimensions = 3, 
                        num_zslices = None, 
                        segmentation = None, 
                        decode_only_cells = True, 
                        labeled_img = None, 
                        num_wav = 3, 
                        synd_decoding = True)
                        #lampfish_decoding = True)
    print('Made Decoding Class')
    
    decoder.run_lampfish_decoding()
    
elif sys.argv[1] == 'debug_decoding_class_lampfish_test':
    decoder = Decoding(data_dir = '/groups/CaiLab/personal/nrezaee/raw/test1', 
                        position = 'MMStack_Pos0.ome.tif', 
                        decoded_dir = 'foo/test_decoding_class/lampfish_test', 
                        locations_dir = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/Dot_Locations/', 
                        position_dir = '/groups/CaiLab/analyses/nrezaee/test1/dot/MMStack_Pos0/', 
                        barcode_dst = None, 
                        barcode_src = None, 
                        bool_decoding_with_previous_dots = False, 
                        bool_decoding_with_previous_locations = False, 
                        bool_fake_barcodes = False, 
                        bool_decoding_individual = 'all', 
                        min_seeds = None, 
                        allowed_diff = None, 
                        dimensions = 3, 
                        num_zslices = None, 
                        segmentation = None, 
                        decode_only_cells = True, 
                        labeled_img = None, 
                        num_wav = 4, 
                        synd_decoding = True, 
                        lampfish_pixel=False)
                        #lampfish_decoding = True)
    print('Made Decoding Class')
    
    decoder.run_lampfish_decoding()



































