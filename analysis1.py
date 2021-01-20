import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob
from load_tiff import tiffy

#Alignment Scripts
#----------------------------
from align_scripts import run_alignment
#----------------------------

#Align Error Script
#----------------------------
from align_errors import align_errors
#----------------------------

#Dot Detection Script
#----------------------------
from dot_detection import main_dot_detection
#----------------------------

#Barcode Script
#----------------------------
from read_barcode import read_barcode
#----------------------------

#Decoding Script
#----------------------------
from decoding.decoding_class import Decoding
from decoding import decoding
from decoding import previous_points_decoding as previous_points_decoding
from decoding import previous_locations_decoding as previous_locations_decoding
#----------------------------

#Segmentation Script
#----------------------------
from segmentation.roi_segment import run_roi
#----------------------------


#Colcalization Test Scripts
#----------------------------
from colocalization import colocalize
#----------------------------

#Chromatic Abberation Scripts
#----------------------------
import chromatic_abberation
from chromatic_abberation import run
#----------------------------

#Analysis
#----------------------------
from analyses.false_positive_rate_analysis import get_false_pos_rate
from analyses.on_off_barcode_plot import get_on_off_barcode_plot
from analyses.hamming_distance import get_hamming_analysis
#----------------------------




if os.environ.get('DATA_PIPELINE_MAIN_DIR') is not None:
    main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']
else:
    raise Exception("The Main Directory env variable is not set. Set DATA_PIPELINE_MAIN_DIR!!!!!!!!")


#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Analysis:
    def __init__(self, experiment_name, analysis_name, personal, position):
        #Set Basic Information
        #--------------------------------------------------------------
        self.experiment_name = experiment_name
        self.personal = personal
        self.analysis_name = analysis_name
        self.position = position
        #--------------------------------------------------------------
        
        #Set Parameters
        #--------------------------------------------------------------
        self.align = None
        self.chromatic_abberration =False
        self.normalization=False
        self.deconvolution=False
        self.get_align_errors = False
        self.dot_detection = False
        self.decoding_across = False
        self.visualize_dots = False
        self.colocalize = False
        self.background_subtraction = False
        self.decoding_with_previous_dots  = False
        self.segmentation = False
        self.decoding_with_previous_locations  = False
        self.fake_barcodes = False 
        self.num_zslices = None
        self.on_off_barcode_analysis = False
        self.false_positive_rate_analysis = False
        self.gaussian_fitting = False
        self.allowed_diff = 1
        self.strictness_dot_detection = 5
        self.dimensions = 3
        self.decoding_individual = 'all'
        self.min_seeds = 'number_of_rounds - 1'
        #--------------------------------------------------------------
        
        
        #Set Directories
        #--------------------------------------------------------------
        self.analysis_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, self.analysis_name)
        self.position_dir = os.path.join(self.analysis_dir, self.position.split('.ome')[0])
        self.decoded_dir = os.path.join(self.position_dir, 'Decoded')
        self.locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
        self.seg_dir = os.path.join(self.position_dir, 'Segmentation')
        self.barcode_dst = os.path.join(self.analysis_dir, 'BarcodeKey')
        self.hamming_dir = os.path.join(self.position_dir, 'Hamming_Analysis')
        
        self.data_dir = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name)
        self.barcode_key_src = os.path.join(self.data_dir, 'barcode_key')
        self.seg_data_dir = os.path.join(self.data_dir, 'segmentation')
        #--------------------------------------------------------------
        
       
    #Set Parameters
    #--------------------------------------------------------------------------------
    def set_alignment_arg(self, align_arg):
        self.align = align_arg.replace(" ", "_")
        
        if '2d' in self.align:
            self.dimensions = 2
            
        print("    Set Alignment to", str(self.align))

    def set_align_errors_true(self):
        self.get_align_errors = True
        print("    Set Alignment Errors", flush=True)
        
    def set_background_subtraction_true(self):
        self.background_subtraction = True
        print("    Set Background Subtraction", flush=True)
        
    def set_chromatic_abberration_true(self):
        self.chromatic_abberration = True
        print("    Set Chromatic Abberration", flush=True)
        
    def set_normalization_true(self):
        self.normalization = True
        print("    Set Normalization", flush=True)
        
    def set_deconvolution_true(self):
        self.deconvolution=True
        print("    Set Deconvolution", flush=True)
        
    def set_dot_detection_arg(self, detection_arg):
        self.dot_detection = detection_arg
        print("    Set Dot Detection to", detection_arg, flush=True)

    def set_decoding_across_true(self):
        self.decoding_across = True
        print("    Set Decoding Across Channels", flush=True)
        
    def set_decoding_with_previous_dots_true(self):
        self.decoding_with_previous_dots  = True
        print("    Set Decoding Channels with Previous Points", flush=True)   

    def set_decoding_with_previous_locations_true(self):
        self.decoding_with_previous_locations  = True
        print("    Set Decoding Channels with Previous Locations", flush=True) 

    def set_decoding_individual(self, individual_arg):
        self.decoding_individual = [int(channel) for channel in individual_arg]
        self.decoding_individual.sort()
        print(f'{type(self.decoding_individual)=}')
        print(f'{self.decoding_individual=}')
        print("    Set Decoding Individual Channels", flush=True)   
        
    def set_visual_dot_detection_true(self):
        self.visualize_dots = True
        print("    Set Visualize Dots", flush=True)
        
    def set_colocalize_true(self):
        self.colocalize = True
        print("    Set Colocalization", flush=True)
        
   
    def set_segmentation_arg(self, segment_arg):
        self.segmentation =segment_arg
        print("    Set Segmentation", flush=True)
        
    def set_fake_barcodes_true(self):
        self.fake_barcodes = True
        print("    Set Fake Barcodes")
        
    def set_on_off_barcode_analysis_true(self):
        self.on_off_barcode_analysis = True
        print("    Set On/Off Barcode Analysis")
        
    def set_false_positive_rate_analysis_true(self):
        self.false_positive_rate_analysis = True
        print("    Set False Positive Rate Analysis")
        
    def set_gaussian_fitting_true(self):
        self.gaussian_fitting= True
        print("    Set Gaussian Fitting True")
        
    def set_allowed_diff_arg(self, allowed_diff_arg):
        self.allowed_diff = int(allowed_diff_arg)
        
        assert self.allowed_diff >=0, "Allowed Diff must be greater than zero."
        assert self.allowed_diff < 10, "Allowed Diff may be to large (greater than 10)."
        
        print("    Set Allowed Diff to", str(self.allowed_diff))
        
    def set_strictness_arg(self, strictness_arg):
        self.strictness_dot_detection = int(strictness_arg)
        
        assert self.strictness_dot_detection >=0, "Strictness must be greater than zero."
        
        print("    Set Strictness to", str(self.strictness_dot_detection))

    def set_min_seeds_arg(self, min_seeds_arg):
        self.min_seeds = int(min_seeds_arg)
        
        assert self.min_seeds >=0, "Min Seeds must be greater than zero."
        
        print("    Set Min Seeds to", str(self.min_seeds))
        
    def set_hamming_analysis_true(self):
        self.hamming_analysis = True
        print("    Set Hamming Analysis True")
    #--------------------------------------------------------------------
    #Finished Setting Parameters
    
    
    #Set functions for analysis
    #--------------------------------------------------------------------
    
    def run_dot_detection_2d(self):
        
        for z in range(self.num_zslices):
            
            #Run Dot Detection
            #--------------------------------------------------------------------
            locations = main_dot_detection.get_dots(self.experiment_name, self.personal, self.position, \
                                               self.analysis_name, self.visualize_dots, self.normalization, \
                                               self.background_subtraction, self.decoding_individual, self.chromatic_abberration, \
                                               self.dot_detection, self.gaussian_fitting, self.strictness_dot_detection, z_slices=z)
    
            #--------------------------------------------------------------------
            
            
            #Set path to save locations
            #--------------------------------------------------------------------
            if not os.path.exists(self.locations_dir ):
                os.makedirs(self.locations_dir )
            
            locations_file_name = 'locations_z_' + str(z) +'.mat'
        
            locations_path = os.path.join(self.locations_dir , locations_file_name)
            #--------------------------------------------------------------------
        
            
            #Save Locations
            #--------------------------------------------------------------------
            print("        Saving Locations to", locations_path, flush=True)
            
    
            sio.savemat(locations_path,{'locations': locations})
            #--------------------------------------------------------------------

    def run_dot_detection(self):
        
        if self.dimensions == 2:
            self.run_dot_detection_2d()
            return None
            
        print("    Getting Dot Locations with", self.dot_detection, flush=True)
        
        #Run Dot Detection
        #--------------------------------------------------------------------
            
        locations = main_dot_detection.get_dots(self.experiment_name, self.personal, self.position, \
                                               self.analysis_name, self.visualize_dots, self.normalization, \
                                               self.background_subtraction, self.decoding_individual, self.chromatic_abberration, \
                                               self.dot_detection, self.gaussian_fitting, self.strictness_dot_detection)

        #--------------------------------------------------------------------
        
        
        #Set path to save locations
        #--------------------------------------------------------------------
        if not os.path.exists(self.locations_dir):
            os.makedirs(self.locations_dir)
        
    
        locations_path = os.path.join(self.locations_dir, 'locations.mat')
        #--------------------------------------------------------------------
    
        
        #Save Locations
        #--------------------------------------------------------------------
        print("        Saving Locations to", locations_path, flush=True)
        

        sio.savemat(locations_path,{'locations': locations})
        #--------------------------------------------------------------------
            
            
    def run_alignment_errors(self):

        #Get alignment errors
        #--------------------------------------------------------------------
        print("    Getting Alignment Errors", flush=True)
        
        errors = align_errors.get_align_errors(self.personal, self.experiment_name, self.position, self.analysis_name, dims_to_align = self.dimensions)
        #--------------------------------------------------------------------
        
        
        #Write Results to Path
        #-----------------------------------------------------
        errors_path  = os.path.join(self.position_dir, 'errors_for_alignment.json')
        
        print("        Saving alignment errors to", errors_path, flush=True)
        with open(errors_path, 'w') as jsonfile:
            json.dump(errors, jsonfile)
        #-----------------------------------------------------
        
    def run_colocalization(self):
        
        #Make directories for colocalization
        #--------------------------------------------------------------------
        print("Running Colocalization Test")
        

        if not os.path.exists(self.locations_dir):
            os.makedirs(self.locations_dir)
        
    
        locations_path = os.path.join(self.locations_dir, 'locations.mat')
                        
        coloc_dir = os.path.join(self.position_dir, 'Colocalization')
                        
        if not os.path.exists(coloc_dir):
            os.makedirs(coloc_dir)
        #--------------------------------------------------------------------
        
        #Run Colocalization
        #--------------------------------------------------------------------
        colocalize.colocalize(locations_path, coloc_dir)
        #--------------------------------------------------------------------
        
        
    def run_decoding_across(self):

        
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_key_src, 'barcode.csv')
        
                                  
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
        
        decoding.decoding(barcode_file_path, locations_path, self.decoded_dir, allowed_diff = self.allowed_diff, min_seeds = self.min_seeds)
        
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
    def run_decoding_individual_2d(self):

        #Loop through each individual channel
        #--------------------------------------------------------------------
        for channel in self.decoding_individual:
        
            #Set Directories for reading barcode key
            #--------------------------------------------------------------------
            barcode_file_name = 'channel_' + str(channel) + '.csv'
            
            barcode_src = os.path.join(self.barcode_key_dst, barcode_file_name)
                                      
            if not os.path.exists(self.barcode_key_src):
                os.makedirs(self.barcode_key_src)
                
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
                            
                locations_file_name = 'locations_z_' + str(z) +'.mat'
                
                locations_path_z = os.path.join(locations_dir, locations_file_name)
                #--------------------------------------------------------------------
            
                
                #Set directories for decoding
                #--------------------------------------------------------------------
                decoding_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, \
                                      self.analysis_name, self.position.split('.ome')[0], 'Decoded')       
                                      
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
            
                #Run decoding for individual channel
                #--------------------------------------------------------------------
                decoding.decoding(barcode_dst, locations_path_z, decoding_dst_for_channel_z, self.allowed_diff, self.min_seeds, self.decoding_individual.index(channel), \
                                  len(self.decoding_individual))
                #--------------------------------------------------------------------


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
            
            barcode_src = os.path.join( barcode_file_name)
            
            
     
            if not os.path.exists(self.barcode_key_dst):
                os.makedirs(self.barcode_key_dst)
                
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
        
            #Run decoding for individual channel
            #--------------------------------------------------------------------
            decoding.decoding(barcode_dst, locations_path, decoding_dst_for_channel, self.decoding_individual.index(channel), \
                              len(self.decoding_individual), allowed_diff= self.allowed_diff, min_seeds = self.min_seeds)
            #--------------------------------------------------------------------
        
        
    def run_chromatic_abberation(self):
        
        beads_src = os.path.join(self.data_dir, 'beads')
        
        t_form_dest = os.path.join(self.analysis_dir, \
                        'Chromatic_Abberation_Correction')
        
        if not os.path.exists(t_form_dest):
            os.makedirs(t_form_dest)
            
        chromatic_abberation.run.run_beads(beads_src, t_form_dest)
        

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
        
        barcode_src = os.path.join(self.barcode_key_src, 'barcode.csv')
                                  
        if not os.path.exists(self.barcode_dst):
            os.makedirs(self.barcode_dst)
            
        barcode_dst = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, \
                                  self.analysis_name,'BarcodeKey', 'barcode.mat')
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
        glob_me = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name, 'locations', '*.mat')
        
        mat_file_paths = glob.glob(glob_me)
        
        assert len(mat_file_paths) == 1, "There can only be one mat file in the locations directory or \
                                         the pipeline cannot determine which mat file has the points."
                                         
        mat_file_path = mat_file_paths[0]
        #--------------------------------------------------------------------
        
        
        #Set directories for barcodes 
        #--------------------------------------------------------------------
        print("Reading Barcodes", flush=True)
        
        barcode_src = os.path.join(self.barcode_key_src, 'barcode.csv')
                                  
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
        
        previous_locations_decoding.decoding(barcode_dst, mat_file_path, decoding_dst, allowed_diff = self.allowed_diff, min_seeds = self.min_seeds)
        
        print("Finished Decoding Across Channels")
        #--------------------------------------------------------------------
        
        
        
    def run_segmentation(self):
        
        # Get Segmentation DIrs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------
        
        
        #If Roi
        #----------------------------------------------
        if 'roi' in self.segmentation.lower():
            
            #Set Directory args
            #----------------------------------------------
            glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')
                                 
            roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)
              
            assert len(roi_zip_file_paths) == 1
              
            roi_zip_file_path = roi_zip_file_paths[0]
        
            decoded_genes_path = os.path.join(self.decoded_dir, 'finalPosList.mat')
            
            barcode_path = os.path.join(self.barcode_key_src, 'barcode.csv')
            #----------------------------------------------
                
            run_roi.run_me(segmented_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes)
        #----------------------------------------------
    
    
    def run_segmentation_individually_2d(self):
    
        if not os.path.exists(self.seg_data_dir):
            os.makedirs(self.seg_data_dir)
             
        if 'roi' in self.segmentation.lower():
            glob_me_for_roi_zips = os.path.join(self.seg_data_sir, '*')
                                 
            roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)
              
            assert len(roi_zip_file_paths) == 1
              
            roi_zip_file_path = roi_zip_file_paths[0]
            
            for channel_num in self.decoding_individual:
                
                #Get Segmentation Dirs
                #----------------------------------------------
                segmented_channel_dir = os.path.join(self.seg_dir, \
                                            'Channel_'+str(channel_num))
                                        
                if not os.path.exists(segmented_channel_dir):
                    os.makedirs(segmented_channel_dir)
                #----------------------------------------------
                
                barcode_path = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name, \
                                        'barcode_key', 'channel_' +str(channel_num)+'.csv')
                    
                for z in range(self.num_zslices):
                    
                    
                    
                    print('-------------------------------------------------------------------')
                    
                    segmented_z_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, \
                                            self.analysis_name, self.position.split('.ome')[0], 'Segmentation', \
                                            'Channel_'+str(channel_num), 'Z_Slice_' +str(z))
                                            
                    if not os.path.exists(segmented_z_dir):
                        os.makedirs(segmented_z_dir)
                
                    decoded_genes_path = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, \
                                            self.analysis_name, self.position.split('.ome')[0], 'Decoded', \
                                            'Channel_'+str(channel_num), 'Z_Slice_'+str(z), 'finalPosList.mat')
                                            
    
                    run_roi.run_me(segmented_z_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes)


    def run_segmentation_individually(self):
        
        if self.dimensions == 2:
            self.run_segmentation_individually_2d()
            return None
        
        # Get Segmentation Dirs
        #----------------------------------------------
        if not os.path.exists(self.seg_data_dir):
            os.makedirs(self.seg_data_dir)
        #----------------------------------------------
        
        
        #----------------------------------------------
        if 'roi' in self.segmentation.lower():
            
            
            #----------------------------------------------
            glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')
                                 
            roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)
              
            assert len(roi_zip_file_paths) == 1
              
            roi_zip_file_path = roi_zip_file_paths[0]
            #----------------------------------------------
            
            
            
            for channel_num in self.decoding_individual:
                
                # Get Segmentation Dirs
                #----------------------------------------------
                segmented_dir = os.path.join(self.seg_dir, 'Channel_'+str(channel_num))
                                        
                if not os.path.exists(segmented_dir):
                    os.makedirs(segmented_dir)
                #----------------------------------------------
                    
                    decoded_genes_path = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, \
                                            self.analysis_name, self.position.split('.ome')[0], 'Decoded', 'Channel_'+str(channel_num), 'finalPosList.mat')
                                            
                    barcode_path = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name, \
                                        'barcode_key', 'channel_' +str(channel_num)+'.csv')
                    
                    run_roi.run_me(segmented_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes)
        #----------------------------------------------
                

    def run_on_off_barcode_analysis(self):
        
        genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'gene_locations_assigned_to_cell.csv')
                                                            
        dst_dir = os.path.join(self.position_dir, 'On_Off_Barcode_Plot')
        
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        get_on_off_barcode_plot(genes_assigned_to_cell_src, dst_dir)
        

    def run_false_positive_rate_analysis(self):
        
        genes_assigned_to_cell_src = os.path.join(self.position_dir, 'Segmentation', 'gene_locations_assigned_to_cell.csv')

        if not os.path.exists(self.false_pos_dir):
            os.makedirs(self.false_pos_dir)
            
        dst_file_path = os.path.join(self.false_pos_dir, 'false_positives.txt')
        
        get_false_pos_rate(genes_assigned_to_cell_src, dst_file_path)
        
    def run_hamming_analysis(self):
        
        genes_assigned_to_cell_src = os.path.join(self.seg_dir, 'gene_locations_assigned_to_cell.csv')
                                                   
        if not os.path.exists(self.hamming_dir):
            os.makedirs(self.hamming_dir)
            
        dest_file_path = os.path.join(self.hamming_dir, 'hamming_distance_analytics.txt')
        
        get_hamming_analysis(genes_assigned_to_cell_src, self.barcode_key_src, dest_file_path)
        
    #--------------------------------------------------------------------------------
    
    
    #Runs the Parameters and functions
    #--------------------------------------------------------------------------------
    def write_results(self, path):
        

        #Get Z slices if two dimensional
        #--------------------------------------------------------------------------------
        if self.dimensions == 2:
            exp_dir = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name)
            
            subdirs = os.listdir(exp_dir)
    
            hyb_dirs = [sub_dir for sub_dir in subdirs if 'Hyb' in sub_dir]         
            
            assert len(hyb_dirs) > 0, "There are not HybCycle Directories in the experiment directory."
            
            hyb_dir = hyb_dirs[0]
            
            sample_tiff_src = os.path.join(exp_dir, hyb_dir, self.position)
            
            sample_tiff = tiffy.load(sample_tiff_src)
            
            self.num_zslices = sample_tiff.shape[0]
        #--------------------------------------------------------------------------------
        
        
        #Alignment
        #--------------------------------------------------------------------------------
        if not self.decoding_with_previous_dots and not self.decoding_with_previous_locations:
            if self.align == None:
                
                offset = run_alignment.run_alignment(self.experiment_name, self.personal, self.position, 'no_align')
                offsets_path = os.path.join(path, 'offsets.json')
            
            else:
                
                offset = run_alignment.run_alignment(self.experiment_name, self.personal, self.position, self.align)
                offsets_path = os.path.join(path, 'offsets.json')
                print("        Saving to", offsets_path, flush=True)
            
            #Write Results to Path
            #-----------------------------------------------------
            with open(offsets_path, 'w') as jsonfile:
                json.dump(offset, jsonfile)
                    
            #-----------------------------------------------------
        #--------------------------------------------------------------------------------
        #End of Alignement
            

        #Get Errors for Alignment
        #--------------------------------------------------------------------------------
        if self.get_align_errors == True:
            self.run_alignment_errors()
        #--------------------------------------------------------------------------------
        
        
        #Get Chromatic Abberation
        #--------------------------------------------------------------------------------
        if self.chromatic_abberration == True:
            self.run_chromatic_abberation()
            
        #--------------------------------------------------------------------------------
        
        #Run Dot Detection
        #--------------------------------------------------------------------------------
        if self.dot_detection != False:
            self.run_dot_detection()
        #--------------------------------------------------------------------------------
        
        
        #Run Visualize Dots
        #--------------------------------------------------------------------------------
        if self.visualize_dots == True and self.dot_detection == False:
            self.run_dot_detection()
        #--------------------------------------------------------------------------------
        
        #Run colocalization test
        #--------------------------------------------------------------------------------
        if self.colocalize == True:
            if self.dot_detection == False:
                self.run_dot_detection()
                
            self.run_colocalization()
        #--------------------------------------------------------------------------------
            
        
        #Run Decoding Across
        #--------------------------------------------------------------------------------
        if self.decoding_across == True:
            if self.dot_detection == False:
                self.run_dot_detection()
                
            self.run_decoding_across()
        #--------------------------------------------------------------------------------
        
        
        #Run Decoding Individual
        #--------------------------------------------------------------------------------

        if not self.decoding_individual == 'all':
            if self.dot_detection == False:
                
                self.run_dot_detection()
                
            print('Past if on decoding indiv')
            self.run_decoding_individual()
        #--------------------------------------------------------------------------------
        
        
        #Run Decoding with previous dots
        #--------------------------------------------------------------------------------
        if self.decoding_with_previous_dots == True:
                
            self.run_decoding_with_previous_dots()        
        #--------------------------------------------------------------------------------
        
        #Run Decoding with previous dots
        #--------------------------------------------------------------------------------
        if self.decoding_with_previous_locations == True:
            
            print('Run decoding previous locations after if statement')
                
            self.run_decoding_with_previous_locations()        
        #--------------------------------------------------------------------------------
        
        #Run Segmentation
        #--------------------------------------------------------------------------------
        print('Before if segementation')
        if self.segmentation !=False:
            print("Pass if Statment of running Segmentation")
            
            if self.decoding_across == True or \
               self.decoding_with_previous_dots == True or \
               self.decoding_with_previous_locations == True:
                
                print("Pass if Statment of running Segmentation")
                self.run_segmentation()      
                
            elif not self.decoding_individual == 'all':
                
                self.run_segmentation_individually()
        #--------------------------------------------------------------------------------
    
        
        #Run On Off Barcode Analysis    
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.on_off_barcode_analysis == True:
            self.run_on_off_barcode_analysis()
        #--------------------------------------------------------------------------------
    
    
        #Run False Positive Rate Analysis    
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.false_positive_rate_analysis == True:
            self.run_false_positive_rate_analysis()
        #--------------------------------------------------------------------------------
        
        
        #Run Hamming Distance Analysis  
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.hamming_analysis == True:
            self.run_hamming_analysis()
        #--------------------------------------------------------------------------------
        
        
    #--------------------------------------------------------------------------------
    #End of running the parameters
            
        
        