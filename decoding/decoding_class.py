import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob
import pandas as pd
import tifffile

from helpers.reorder_hybs import get_and_sort_hybs
from segmentation.cellpose_segment.helpers.get_cellpose_labeled_img import get_labeled_img_cellpose

#Barcode Script
#----------------------------
from read_barcode import read_barcode
#----------------------------


#Decoding Script
#----------------------------
from decoding import decoding
from decoding import decoding_parallel
from decoding import previous_points_decoding as previous_points_decoding
from decoding import previous_locations_decoding as previous_locations_decoding
#----------------------------


#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Decoding:
    def __init__(self, data_dir, position, decoded_dir, locations_dir, position_dir, barcode_dst, barcode_src, bool_decoding_with_previous_dots, bool_decoding_with_previous_locations, \
                    bool_fake_barcodes, bool_decoding_individual, min_seeds, allowed_diff, dimensions, num_zslices, segmentation, decode_only_cells):
        
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
        locations_path = os.path.join(self.locations_dir, 'locations.mat')
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
            
            if self.seg == "roi":
                labeled_img = tifffile.imread('/home/nrezaee/sandbox/multiprocessing/decoding/roi.tiff')
            elif self.seg == "cellpose":
            
                #Run Decoding Across Channels
                #--------------------------------------------------------------------
                print("Running Decoding Across Channels")
                labeled_img = self.labeled_img_from_tiff_dir()
                
            decoding_parallel.decoding(barcode_file_path, locations_path, labeled_img, self.decoded_dir, self.allowed_diff, \
                self.min_seeds, decode_only_cells = self.decode_only_cells)
                
            return labeled_img
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
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
        locations_path = os.path.join(self.locations_dir, 'locations.mat')
        #--------------------------------------------------------------------
        
        #Set Directory for Decoding
        #--------------------------------------------------------------------
        if not os.path.exists(self.decoded_dir):
            os.makedirs(self.decoded_dir)
        #--------------------------------------------------------------------
        
        #Get Labeled Img
        #--------------------------------------------------------------------
        if self.seg != False:

            if self.seg == "roi":
                labeled_img = self.labeled_img_from_tiff_dir()
                    
            elif self.seg == "cellpose":
            
                print("Running Decoding Across Channels")
                labeled_img = self.labeled_img_from_tiff_dir()
        #--------------------------------------------------------------------
        
        for z in range(self.num_zslices):
        
            #Set file path for locations
            #--------------------------------------------------------------------
            locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
                        
            locations_file_name = 'locations_z_' + str(z) +'.mat'
            
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
                    
                decoding_parallel.decoding(barcode_file_path, locations_path_z, labeled_img, decoding_dst_z, self.allowed_diff,  \
                    self.min_seeds, decode_only_cells = self.decode_only_cells)
            print("Finished Decoding Across Channels")
            #--------------------------------------------------------------------
            
        self.combine_decode_z_s(self.decoded_dir)
        return labeled_img
        
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
            
            #Get Labeled Img
            #--------------------------------------------------------------------
            if self.seg != False:
    
                if self.seg == "roi":
                    labeled_img = tifffile.imread('/home/nrezaee/sandbox/multiprocessing/decoding/roi.tiff')
                elif self.seg == "cellpose":
                    print("Running Decoding Across Channels")
                    labeled_img = self.labeled_img_from_tiff_dir()
            #--------------------------------------------------------------------
            
            for z in range(self.num_zslices):
            
                #Set file path for locations
                #--------------------------------------------------------------------
                locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
                            
                locations_file_name = 'locations_z_' + str(z) +'.mat'
                
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
                    decoding_parallel.decoding(barcode_dst, locations_path_z, labeled_img, decoding_dst_for_channel_z, self.allowed_diff, self.min_seeds, \
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
            locations_path = os.path.join(self.locations_dir, 'locations.mat')
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
                decoding.decoding(barcode_dst, locations_path, decoding_dst_for_channel, self.allowed_diff, self.min_seeds, self.decoding_individual.index(channel), \
                                  len(self.decoding_individual))
                #--------------------------------------------------------------------
            else:
                
                #Run Decoding Across Channels
                #--------------------------------------------------------------------
                print("Running Decoding Across Channels")
                #labeled_img = self.labeled_img_from_tiff_dir()
                labeled_img = self.labeled_img_from_tiff_dir()
                
                decoding_parallel.decoding(barcode_dst, locations_path, labeled_img, decoding_dst_for_channel, self.allowed_diff, self.min_seeds, \
                    self.decoding_individual.index(channel), len(self.decoding_individual), decode_only_cells = self.decode_only_cells)
                    
                return labeled_img
                
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