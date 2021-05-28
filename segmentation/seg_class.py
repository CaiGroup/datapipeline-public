import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob
import tifffile as tf


#Segmentation Script
#----------------------------
from segmentation.roi_segment import run_roi
from segmentation.cellpose_segment import run_cellpose
from segmentation.post_processing.get_post_processing import save_labeled_img
from segmentation.visualization.visual_seg import get_label_img_visuals
#----------------------------


main_dir = '/groups/CaiLab'
# if os.environ.get('DATA_PIPELINE_MAIN_DIR') is not None:
#     main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']
# else:
#     raise Exception("The Main Directory env variable is not set. Set DATA_PIPELINE_MAIN_DIR!!!!!!!!")


#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Segmentation:
    def __init__(self, data_dir, position, seg_dir, decoded_dir, locations_dir, barcode_dst, barcode_src, \
                    bool_fake_barcodes, bool_decoding_individual, num_z_slices, seg_type, seg_data_dir, dimensions, num_zslices, \
                    labeled_img, edge_dist, dist_between_nuclei, bool_cyto_match, area_tol, cyto_channel_num, \
                    get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, flow_threshold, cell_prob_threshold):

        self.data_dir = data_dir
        self.position = position
        self.seg_dir = seg_dir
        self.locations_dir = locations_dir        
        self.decoded_dir = decoded_dir
        self.barcode_dst = barcode_dst
        self.barcode_src = barcode_src
        self.fake_barcodes = bool_fake_barcodes 
        self.decoding_individual = bool_decoding_individual
        self.num_z_slices = num_z_slices
        self.seg_type = seg_type.lower()
        self.seg_dir = seg_dir
        self.seg_data_dir = seg_data_dir
        self.dimensions = dimensions
        self.num_zslices = num_zslices
        self.labeled_img = labeled_img
        self.edge_dist = edge_dist
        self.dist_between_nuclei = dist_between_nuclei
        self.bool_cyto_match = bool_cyto_match
        self.area_tol = area_tol
        self.cyto_channel_num = cyto_channel_num
        self.get_nuclei_img = get_nuclei_img
        self.get_cyto_img = get_cyto_img
        self.labeled_img = labeled_img
        self.num_wav = num_wav
        self.nuclei_radius = nuclei_radius
        self.flow_threshold = flow_threshold
        self.cell_prob_threshold = cell_prob_threshold
        
    def combine_seg_z_s(seg_channel_dir):
    
        #Get Csv's
        #-----------------------------------------------------
        glob_me = os.path.join(seg_channel_dir, '*', 'gene_locations_assigned_to_cell.csv')
        
        csv_s = glob.glob(glob_me)
        
        assert len(csv_s) > 0, "There are no csv's in the Z Slices for segmentation"
        #-----------------------------------------------------
        
        
        #Concatenate Csv's
        #-----------------------------------------------------
        df_concat = pd.read_csv(csv_s[0])
        
        for i in range(1, len(csv_s)):
            df_concat_me = pd.read_csv(csv_s[i])
            
            df_concat = pd.concat([df_concat, df_concat_me])
        #-----------------------------------------------------
        
        
        #Save Concatenated Csv
        #-----------------------------------------------------
        concat_dst = os.path.join(seg_channel_dir, 'gene_locations_assigned_to_cell.csv')
        df_concat.to_csv(concat_dst, index=False)
        #-----------------------------------------------------
        
         
    def run_segmentation_across(self):
        
        # Get Segmentation DIrs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------
        
        #Get Decoded genes path
        #----------------------------------------------
        decoded_genes_glob = os.path.join(self.decoded_dir, '*unfiltered.csv')
        
        decoded_genes_paths = glob.glob(decoded_genes_glob)
        
        assert len(decoded_genes_paths) == 1, "There should be exactly one file with *unfiltered.csv"
        
        decoded_genes_path = decoded_genes_paths[0]
        #----------------------------------------------
        
        #If Roi
        #----------------------------------------------
        if 'roi' in self.seg_type:
            
            #Set Directory args
            #----------------------------------------------
            glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')
                                 
            roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)
              
            assert len(roi_zip_file_paths) == 1
              
            roi_zip_file_path = roi_zip_file_paths[0]
            
            barcode_path = os.path.join(self.barcode_src, 'barcode.csv')
            #----------------------------------------------
                
            run_roi.run_me(self.seg_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes, self.num_zslices)
             #----------------------------------------------
        
        elif "cellpose" in self.seg_type:
            
                
            run_cellpose.run_me(self.data_dir, self.seg_dir, decoded_genes_path, self.position, self.labeled_img)
            #----------------------------------------------

    def run_segmentation_non_barcoded(self):
        
        # Get Segmentation DIrs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------
        
        #Get Decoded genes path
        #----------------------------------------------
        decoded_genes_path = os.path.join(self.decoded_dir, 'sequential_decoding_results.csv')
        #----------------------------------------------
            
        run_cellpose.run_me(self.data_dir, self.seg_dir, decoded_genes_path, self.position, self.labeled_img)
    
    

    def run_segmentation_individually(self):
        

        # Get Segmentation Dirs
        #----------------------------------------------
        for channel_num in self.decoding_individual:
            
            # Get Segmentation Dirs
            #----------------------------------------------
            segmented_dir = os.path.join(self.seg_dir, 'Channel_'+str(channel_num))
                                    
            if not os.path.exists(segmented_dir):
                os.makedirs(segmented_dir)
            #----------------------------------------------
            
            #Get Decoded genes path
            #----------------------------------------------
            decoded_genes_glob = os.path.join(self.decoded_dir, 'Channel_'+str(channel_num),'*unfiltered.csv')
            print(f'{decoded_genes_glob=}')
            decoded_genes_paths = glob.glob(decoded_genes_glob)
            print(f'{decoded_genes_paths=}')
            assert len(decoded_genes_paths) == 1, "There should be exactly one file with *unfiltered.csv"
            
            decoded_genes_path = decoded_genes_paths[0]
            #----------------------------------------------
            
     
            
            if 'roi' in self.seg_type:
                
                barcode_path = os.path.join(self.barcode_src, 'channel_' +str(channel_num)+'.csv')
                #----------------------------------------------
                glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')
                                     
                roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)
                  
                assert len(roi_zip_file_paths) == 1
                  
                roi_zip_file_path = roi_zip_file_paths[0]
                #----------------------------------------------
                run_roi.run_me(segmented_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes,  self.num_zslices)
        
            elif "cellpose" in self.seg_type:
                
                print(f'{self.labeled_img.shape=}')
                
                run_cellpose.run_me(self.data_dir, segmented_dir, decoded_genes_path, self.position, self.labeled_img)
                #----------------------------------------------
                
    
    def retrieve_labeled_img(self):
        
        # Get Segmentation Dirs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------
        
        label_img_path = save_labeled_img(self.data_dir, self.seg_dir, self.position, self.edge_dist, self.dist_between_nuclei,  \
            self.bool_cyto_match, self.area_tol, self.cyto_channel_num, self.get_nuclei_img, self.get_cyto_img, self.num_wav, \
            self.nuclei_radius, self.num_zslices, self.flow_threshold, self.cell_prob_threshold)
        
        print(f'{label_img_path=}')
        get_label_img_visuals(label_img_path, self.data_dir, self.position, self.num_wav)
        
        labeled_img = tf.imread(label_img_path)
        
        return labeled_img
        
        

 
                