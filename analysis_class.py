import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob
import logging
import time
from datetime import datetime
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
from dot_detection.dot_detection_class import Dot_Detection
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
from segmentation.seg_class import Segmentation
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

#Post Analyses
#----------------------------
from post_analyses.post_analysis_class import Post_Analyses
#----------------------------

#LOgging Time
#----------------------------
from timer import timer_tools
import timer
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
        self.radial_center= False	
        self.hamming_analysis = False
        self.allowed_diff = 1
        self.strictness_dot_detection = 5
        self.dimensions = 3
        self.decoding_individual = 'all'
        self.min_seeds = 'number_of_rounds - 1'
        self.labeled_img = None
        self.edge_dist = 0 
        self.dist_between_nuclei = 0 
        self.bool_cyto_match= False
        self.nuclei_erode = 0
        self.cyto_erode = 0
        self.decode_only_cells = False
        self.nbins = 100
        self.threshold = 300
        self.cyto_channel_num = -2
        self.get_nuclei_seg = False
        self.get_cyto_seg = False
        #--------------------------------------------------------------
        
        
        #Set Directories
        #--------------------------------------------------------------
        self.analysis_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, self.analysis_name)
        self.position_dir = os.path.join(self.analysis_dir, self.position.split('.ome')[0])
        self.logging_pos = os.path.join(self.position_dir, 'Logging.txt')
        self.decoded_dir = os.path.join(self.position_dir, 'Decoded')
        self.locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
        self.seg_dir = os.path.join(self.position_dir, 'Segmentation')
        self.barcode_dst = os.path.join(self.analysis_dir, 'BarcodeKey')
        self.hamming_dir = os.path.join(self.position_dir, 'Hamming_Analysis')
        self.false_pos_dir = os.path.join(self.position_dir, 'False_Positive_Rate_Analysis')
        self.logging_plot_dst = os.path.join(self.position_dir, 'Time_Analysis_Plot.png')
        
        self.data_dir = os.path.join(main_dir, 'personal', self.personal, 'raw', self.experiment_name)
        self.barcode_key_src = os.path.join(self.data_dir, 'barcode_key')
        self.seg_data_dir = os.path.join(self.data_dir, 'segmentation')
        self.locations_data_dir = os.path.join(self.data_dir, 'locations')
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
        
    def set_hamming_analysis_true(self):
        self.hamming_analysis = True
        print("    Set Hamming")
        
    def set_gaussian_fitting_true(self):
        self.gaussian_fitting= True
        print("    Set Gaussian Fitting True")

    def set_radial_center_true(self):
        self.radial_center= True
        print("    Set Radial Center True")
       
    def set_allowed_diff_arg(self, allowed_diff_arg):
        self.allowed_diff = int(allowed_diff_arg)
        
        assert self.allowed_diff >=0, "Allowed Diff must be greater than zero."
        assert self.allowed_diff < 10, "Allowed Diff may be to large (greater than 10)."
        
        print("    Set Allowed Diff to", str(self.allowed_diff))
        
    def set_strictness_arg(self, strictness_arg):
        self.strictness_dot_detection = int(strictness_arg)
        
     #   assert self.strictness_dot_detection >=0, "Strictness must be greater than zero."
        
        print("    Set Strictness to", str(self.strictness_dot_detection))

    def set_min_seeds_arg(self, min_seeds_arg):
        self.min_seeds = int(min_seeds_arg)
        
        assert self.min_seeds >=0, "Min Seeds must be greater than zero."
        
        print("    Set Min Seeds to", str(self.min_seeds))
        
    def set_dist_between_nuclei_arg(self, dist_arg):
        self.dist_between_nuclei = int(dist_arg)
        
        print("    Set Distance Between Nuclei to", str(self.dist_between_nuclei))
        
    def set_edge_deletion_arg(self, edge_dist):
        self.edge_dist = edge_dist
        print("    Set Edges to Delete to", str(self.edge_dist))
        
    def set_all_post_analyses_true(self):
        self.hamming_analysis = True
        on_off_barcode_analysis = True
        self.false_positive_rate_analysis = True
        self.fake_barcodes = True
        
        print("    Set Fake Barcodes")
        print("    Set Hamming Analysis True")
        print("    Set False Positive Rate Analysis")
        print("    Set On/Off Barcode Analysis")
        
    def set_nucleus_erode_arg(self, nucleus_erode_arg):
        self.nucleus_erode = int(nucleus_erode_arg)
        
        print("    Set Nucleus Erode to", str(self.nucleus_erode))

    def set_cyto_erode_arg(self, cyto_erode_arg):
        self.cyto_erode = int(cyto_erode_arg)
        
        print("    Set Cytoplasm Erode to", str(self.cyto_erode))
        
    def set_nuclei_cyto_match_true(self):
        self.bool_cyto_match= True
        print("    Set Nuclei Cytoplasm Matching to True")
        
    def set_decode_only_cells_true(self):
        self.decode_only_cells= True
        print("    Set Decode Only Cells to True")
        
    def set_nbins_arg(self, nbins_arg):
        self.nbins = int(nbins_arg)
        
        print("    Set Number of Bins to", str(self.nbins))
    
    def set_threshold_arg(self, threshold_arg):
        self.threshold = int(threshold_arg)
        
        print("    Set Threshold to", str(self.threshold))
        
    def set_cyto_channel_arg(self, cyto_arg):
        self.cyto_channel_num = int(cyto_arg)
        
        print("    Set Cytoplasm Channel Number to", str(self.cyto_channel_num))
        
    def set_nuclei_labeled_img_true(self):
        self.get_nuclei_seg = True
        
        print("    Set to Get Nuclei Labeled Image")

    def set_cyto_labeled_img_true(self):
        self.get_cyto_seg = True
        
        print("    Set to Get Cyto Labeled Image")
    #--------------------------------------------------------------------
    #Finished Setting Parameters
    
    
    #Set functions for analysis
    #--------------------------------------------------------------------
    def run_dot_detection(self):
        
        dot_detector = Dot_Detection(self.experiment_name, self.personal, self.position, self.locations_dir, \
                                               self.analysis_name, self.visualize_dots, self.normalization, \
                                               self.background_subtraction, self.decoding_individual, self.chromatic_abberration, \
                                               self.dot_detection, self.gaussian_fitting, self.strictness_dot_detection, self.dimensions, \
                                               self.radial_center, self.num_zslices, self.nbins, self.threshold)
                   
        timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                
        
        if self.dimensions == 2:
            
            dot_detector.run_dot_detection_2d()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
            return None
        
        
        dot_detector.run_dot_detection()
        timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
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
        
    def run_chromatic_abberation(self):
        
        beads_src = os.path.join(self.data_dir, 'beads')
        
        t_form_dest = os.path.join(self.analysis_dir, \
                        'Chromatic_Abberation_Correction')
        
        if not os.path.exists(t_form_dest):
            os.makedirs(t_form_dest)
            
        chromatic_abberation.run.run_beads(beads_src, t_form_dest)
        
    #Runs the Parameters and functions
    #--------------------------------------------------------------------------------
    def write_results(self, path):
        
        
        #Start Logging
        #--------------------------------------------------------------------------------
        self.start_time = timer_tools.start_logging(self.logging_pos)
        #--------------------------------------------------------------------------------
        
        
        #Declare Segmentation
        #--------------------------------------------------------------------------------
        if self.segmentation != False:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Segmentation')
            segmenter = Segmentation(self.data_dir, self.position, self.seg_dir, self.decoded_dir, self.locations_dir, self.barcode_dst, self.barcode_key_src, \
                        self.fake_barcodes, self.decoding_individual, self.num_zslices, self.segmentation, self.seg_data_dir, self.dimensions, self.num_zslices, \
                        self.labeled_img, self.edge_dist, self.dist_between_nuclei, self.bool_cyto_match, self.nuclei_erode, self.cyto_erode, self.cyto_channel_num, \
                        self.get_nuclei_seg, self.get_cyto_seg)
        
            self.labeled_img = segmenter.retrieve_labeled_img()
            print('Shape after Seg in Analysis Class: ' +  str(self.labeled_img.shape))
             
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Segmentation')
        #--------------------------------------------------------------------------------
            
        #Get Z slices if two dimensional
        #--------------------------------------------------------------------------------
        #if self.dimensions == 2:
        if not self.decoding_with_previous_locations:
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
        if self.align !=None or self.dot_detection != False or self.decoding_across == True or \
            self.decoding_individual != 'all':
                
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Alignment')
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
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Alignment')
        #--------------------------------------------------------------------------------
        #End of Alignement
            

        #Get Errors for Alignment
        #--------------------------------------------------------------------------------
        if self.get_align_errors == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Alignment Errors')
            self.run_alignment_errors()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Alignment Errors')
        #--------------------------------------------------------------------------------
        
        
        #Get Chromatic Abberation
        #--------------------------------------------------------------------------------
        if self.chromatic_abberration == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Chromatic Abberation')
            self.run_chromatic_abberation()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Chromatic Abberation')
        #--------------------------------------------------------------------------------
        
        #Run Dot Detection
        #--------------------------------------------------------------------------------
        if self.dot_detection != False:
            self.run_dot_detection()
        #--------------------------------------------------------------------------------
        
        #While labeled img is not finished
        
        #labeled_img = fucntion
        
            
        #Declare Decoding Class if needed
        #--------------------------------------------------------------------------------
        if self.decoding_across == True or self.decoding_individual != 'all' \
        or self.decoding_with_previous_dots == True or self.decoding_with_previous_locations == True:
            
            print('Shape before decoding in Analysis Class: ' +  str(self.labeled_img.shape))
            
            decoder = Decoding(self.data_dir, self.position, self.decoded_dir, self.locations_dir, self.position_dir, self.barcode_dst, \
                self.barcode_key_src, self.decoding_with_previous_dots, self.decoding_with_previous_locations, self.fake_barcodes, \
                self.decoding_individual, self.min_seeds, self.allowed_diff, self.dimensions, self.num_zslices, self.segmentation, \
                self.decode_only_cells, self.labeled_img)
        #--------------------------------------------------------------------------------
        
        #Run Decoding with previous dots
        #--------------------------------------------------------------------------------
        if self.decoding_with_previous_dots == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding With Previous Points')
            decoder.run_decoding_with_previous_dots()        
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding With Previous Points')
        #--------------------------------------------------------------------------------
        
        #Run Decoding with previous locations
        #--------------------------------------------------------------------------------
        if self.decoding_with_previous_locations == True:
            
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding With Previous Locations')
            decoder.run_decoding_with_previous_locations()     
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding With Previous Locations')
        #--------------------------------------------------------------------------------
        
        
        #Run Decoding Individual
        #--------------------------------------------------------------------------------
        if not self.decoding_individual == 'all':
            if self.dot_detection == False:
                timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                self.run_dot_detection()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
                
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding Individual')
            self.labeled_img = decoder.run_decoding_individual()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding Individual')
        #--------------------------------------------------------------------------------

        #Run Decoding Across
        #--------------------------------------------------------------------------------
        if self.decoding_across == True:
            if self.dot_detection == False:
                timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                self.run_dot_detection()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
                
            
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding Across')
            self.labeled_img = decoder.run_decoding_across()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding Across')
        #--------------------------------------------------------------------------------
        
        
        # #Declare Segmentation
        # #--------------------------------------------------------------------------------
        # if self.segmentation != False:
        #     timer_tools.logg_elapsed_time(self.start_time, 'Starting Segmentation')
        #     segmenter = Segmentation(self.data_dir, self.position, self.seg_dir, self.decoded_dir, self.locations_dir, self.barcode_dst, self.barcode_key_src, \
        #                 self.fake_barcodes, self.decoding_individual, self.num_zslices, self.segmentation, self.seg_data_dir, self.dimensions, self.num_zslices, \
        #                 self.labeled_img, self.edge_dist, self.dist_between_nuclei, self.bool_cyto_match, self.nuclei_erode, self.cyto_erode)
        
        #     if self.decoding_across == True or \
        #         self.decoding_with_previous_dots == True or \
        #         self.decoding_with_previous_locations == True:
                
        #         segmenter.run_segmentation_across()      

        #     elif not self.decoding_individual == 'all':
                
        #         print('Running Segmentation Individual')
        #         segmenter.run_segmentation_individually()
                
        #     elif self.segmentation == 'cellpose':
        #         segmenter.retrieve_labeled_img()
             
        #     timer_tools.logg_elapsed_time(self.start_time, 'Ending Segmentation')
        # #--------------------------------------------------------------------------------
    
        
        #Make Post Analysis
        #--------------------------------------------------------------------------------
        if self.segmentation != False and (self.on_off_barcode_analysis == True or self.false_positive_rate_analysis == True or self.hamming_analysis == True): 
            post_analysis = Post_Analyses(self.position_dir, self.false_pos_dir, self.seg_dir, self.hamming_dir, self.fake_barcodes, self.barcode_key_src, \
                                self.num_zslices, self.segmentation, self.decoding_individual)
        #--------------------------------------------------------------------------------
        
        
        #Run On Off Barcode Analysis    
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.on_off_barcode_analysis == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting On Off Barcode Plot Analysis')
            if self.decoding_across == True:
                post_analysis.run_on_off_barcode_analysis_across()
            elif self.decoding_individual!=all:
                post_analysis.run_on_off_barcode_analysis_indiv()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending  On Off Barcode Plot Analysis')
        #--------------------------------------------------------------------------------
    
    
        #Run False Positive Rate Analysis    
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.false_positive_rate_analysis == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting False Positive Rate')
            if self.decoding_across ==True:
                post_analysis.run_false_positive_rate_analysis_across()
            elif self.decoding_individual!=all:
                post_analysis.run_false_positive_rate_analysis_indiv()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending False Positive Rate')
        #--------------------------------------------------------------------------------
        
        
        #Run Hamming Distance Analysis  
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.hamming_analysis == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Hamming Analysis')
            if self.decoding_across == True:
                post_analysis.run_hamming_analysis_across()
            elif self.decoding_individual !=all:
                post_analysis.run_hamming_analysis_indiv()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Hamming Analysis')
        #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    #End of running the parameters
            
        
        
