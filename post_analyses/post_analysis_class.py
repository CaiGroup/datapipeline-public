import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob



#Analysis
#----------------------------
from post_analyses.false_positive_rate_analysis import get_false_pos_rate_post_seg, get_false_pos_rate_pre_seg
from post_analyses.on_off_barcode_plot import get_on_off_barcode_plot
from post_analyses.hamming_distance import get_hamming_analysis
#from analyses.post_analysis_class import Post_Analyses
#----------------------------


if os.environ.get('DATA_PIPELINE_MAIN_DIR') is not None:
    main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']
else:
    raise Exception("The Main Directory env variable is not set. Set DATA_PIPELINE_MAIN_DIR!!!!!!!!")


#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Post_Analyses:
    def __init__(self, position_dir, false_pos_dir, seg_dir, hamming_dir, bool_fake_barcodes, barcode_key_src, num_zslices, segmentation, channels):

        #self.start_time = start_time
        self.position_dir = position_dir
        self.false_pos_dir = false_pos_dir
        self.seg_dir = seg_dir
        self.hamming_dir = hamming_dir
        self.fake_barcodes = bool_fake_barcodes 
        self.barcode_key_src = barcode_key_src
        self.segmentation = segmentation
        self.channels = channels

        
    #Run On Off Barcode Plot Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_on_off_barcode_analysis_across(self):
        
        if segmentation != False:
            genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'gene_locations_assigned_to_cell.csv')
                                                                
            dst_dir = os.path.join(self.position_dir, 'On_Off_Barcode_Plot')
            
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            
            get_on_off_barcode_plot(genes_assigned_to_cell_src, dst_dir)
    #--------------------------------------------------------------------------------
    
    #Run On Off Barcode Plot Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_on_off_barcode_analysis_indiv(self):
        
        if segmentation != False:
            
            for channel in self.channels:
                
                genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'Channel_' + str(channel) + 'gene_locations_assigned_to_cell.csv')
                                                                    
                dst_dir = os.path.join(self.position_dir, 'On_Off_Barcode_Plot')
                
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                    
                dst_dir_channel = os.path.join(dst_dir, 'Channel_'+ str(channel))
                
                
                if not os.path.exists(dst_dir_channel):
                    os.makedirs(dst_dir_channel)        
                
                get_on_off_barcode_plot(genes_assigned_to_cell_src, dst_dir_channel)
    #--------------------------------------------------------------------------------
    
    #Run False Positive Rate Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_false_positive_rate_analysis_across(self):

        #RUn for Segmentation
        #----------------------------------------------------------------------------------
        if self.segmentation != False:
            genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'gene_locations_assigned_to_cell.csv')
    
            if not os.path.exists(self.false_pos_dir):
                os.makedirs(self.false_pos_dir)
                
            dst_file_path = os.path.join(self.false_pos_dir, 'false_positives_after_segmentation.txt')
            
            get_false_pos_rate_post_seg(genes_assigned_to_cell_src, dst_file_path)
        #----------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------
    
    #Run False Positive Rate Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_false_positive_rate_analysis_indiv(self):

        #RUn for Segmentation
        #----------------------------------------------------------------------------------
        if self.segmentation != False:
            for channel in self.channels:
                
                genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'Channel_' + str(channel), 'gene_locations_assigned_to_cell.csv')

                if not os.path.exists(self.false_pos_dir):
                    os.makedirs(self.false_pos_dir)
                    
                dst_dir = os.path.join(self.false_pos_dir, 'Channel_'+ str(channel))
                
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)

                dst_file_path = os.path.join(dst_dir,'false_positives_after_segmentation.txt')
                
            get_false_pos_rate_post_seg(genes_assigned_to_cell_src, dst_file_path)
        #----------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------
        
    #Run Hamming Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_hamming_analysis_across(self):
        
        if self.segmentation != False:
            genes_assigned_to_cell_src = os.path.join(self.seg_dir, 'gene_locations_assigned_to_cell.csv')
                                                       
            if not os.path.exists(self.hamming_dir):
                os.makedirs(self.hamming_dir)
                
            dest_file_path = os.path.join(self.hamming_dir, 'hamming_distance_analytics.txt')
            
            barcode_src = os.path.join(self.barcode_key_src, 'barcode.csv')
            
            get_hamming_analysis(genes_assigned_to_cell_src, barcode_src, dest_file_path)
            
    #--------------------------------------------------------------------------------
    
    #Run Hamming Analysis for Segmented Genes
    #--------------------------------------------------------------------------------
    def run_hamming_analysis_indiv(self):
        
        if self.segmentation != False:
            
            for channel in self.channels:
                
                genes_assigned_to_cell_src = os.path.join(self.seg_dir, 'Channel_'+ str(channel), 'gene_locations_assigned_to_cell.csv')
                                                           
                if not os.path.exists(self.hamming_dir):
                    os.makedirs(self.hamming_dir)
                    
                dst_dir = os.path.join(self.hamming_dir,  'Channel_'+ str(channel))
                
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                
                dest_file_path = os.path.join(dst_dir, 'hamming_distance_analytics.txt')
                
                barcode_src = os.path.join(self.barcode_key_src, 'channel_' +str(channel) +'.csv')
                
                get_hamming_analysis(genes_assigned_to_cell_src, barcode_src, dest_file_path)
    #--------------------------------------------------------------------------------
    
    
    
    
    
    
    
    