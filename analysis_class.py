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
import shutil
# sys.path.insert(0, os.getcwd())

print('Current Directory:', os.getcwd())
#Import things to be done after all positions
#-----------------------------------------------------
from helpers.send_email_notif import send_finished_notif, are_logs_finished
from helpers.combine_all_pos_locs import combine_locs_csv_s
from helpers.combine_decoded_genes_all_pos import combine_pos_genes
from helpers.sync_specific_analysis import send_analysis_to_onedrive
from helpers.get_correlation_plots import get_correlated_positions
#-----------------------------------------------------

#Alignment Scripts
#----------------------------
from align_scripts import run_alignment
from align_scripts import fiducial_alignment
from align_scripts.dapi_visual_check.dapi_visual_check import get_stacked_dapi_s_align_check
#----------------------------

#Align Error Script
#----------------------------
from align_errors import align_errors
#----------------------------

#Dot Detection Script
#----------------------------
print('Current Directory:', os.getcwd())
from dot_detection.dot_detection_class4 import Dot_Detection
#----------------------------

#Barcode Script
#----------------------------
from read_barcode import read_barcode
#----------------------------

#Decoding Script
#----------------------------
from decoding.decoding_class import Decoding
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




main_dir = '/groups/CaiLab'



#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Analysis:
    def __init__(self, experiment_name, analysis_name, personal, position, email):
        #Set Basic Information
        #--------------------------------------------------------------
        self.experiment_name = experiment_name
        self.personal = personal
        self.analysis_name = analysis_name
        self.position = position
        self.email = email
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
        self.threshold = .001
        self.cyto_channel_num = -2
        self.get_nuclei_seg = False
        self.get_cyto_seg = False
        self.area_tol = 0
        self.num_wav = 4
        self.locs_src = None
        self.num_z = None
        self.dot_radius = 1
        self.decoding_non_barcoded = False
        self.overlap=1
        self.num_radii = 2
        self.radius_step = 1
        self.debug_dot_detection = False
        self.synd_decoding = False
        self.lampfish_decoding = False
        self.lampfish_pixel = False
        self.nuclei_radius = 0
        self.cell_prob_threshold = 0
        self.flow_threshold = .4
        self.min_weight_adcg = 600.0
        self.final_loss_adcg = 1000.0
        self.max_iters_adcg = 200
        self.max_cd_iters = 10
        self.nuclei_channel_num = -1
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
            
        print("    Set Alignment to", str(self.align))

    def set_align_errors_true(self):
        self.get_align_errors = True
        print("    Set Alignment Errors", flush=True)
        
    def set_background_subtraction_true(self):
        self.background_subtraction = True
        background_file = os.path.join(self.data_dir, 'final_background',self.position)
        assert os.path.isfile(background_file), "The background file for subtraction is missing at " + str(background_file) 
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
        if self.dot_detection == 'matlab 3d':
            self.threshold = 300
        print("    Set Dot Detection to", detection_arg, flush=True)

    def set_decoding_across_true(self):
        self.decoding_across = True
        print("    Set Decoding Across Channels", flush=True)

    def set_non_barcoded_decoding_true(self):
        self.decoding_non_barcoded = True
        print("    Set Decoding Non Barcoded", flush=True)
        
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
        self.on_off_barcode_analysis = True
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
        self.threshold = float(threshold_arg)
        
        print("    Set Threshold to", str(self.threshold))
        
    def set_cyto_channel_arg(self, cyto_arg):
        self.cyto_channel_num = int(float(cyto_arg))
        
        print("    Set Cytoplasm Channel Number to", str(self.cyto_channel_num))
        
    def set_nuclei_labeled_img_true(self):
        self.get_nuclei_seg = True
        
        print("    Set to Get Nuclei Labeled Image")

    def set_cyto_labeled_img_true(self):
        self.get_cyto_seg = True
        
        print("    Set to Get Cyto Labeled Image")
        
    def set_area_tol_arg(self, area_tol):
        self.area_tol = float(area_tol)
        
        print("    Set Matching Area Tolerance to", str(self.area_tol))
        
    def set_num_wavelengths_arg(self, num_wav):
        self.num_wav = float(num_wav)
        
        print("    Set Number of Wavelengths to", str(self.num_wav))
        
    def set_dimensions_arg(self, dims):
        self.dimensions = int(dims)
        
        print("    Set Dimensions to", str(self.dimensions))
        
    def set_z_slices_arg(self, z_slices):
        self.num_z = float(z_slices)
        
        print("    Set Z Slices to", str(self.num_z))
        
    def set_dot_radius_arg(self, dot_radius):
        self.dot_radius = float(dot_radius)
        
        print("    Set Dot Radius to", str(self.dot_radius))
        
    def set_dot_overlap_arg(self, overlap):
        self.overlap = float(overlap)
        
        print("    Set Overlap to", str(self.overlap))
        
    def set_num_radii_arg(self, num_radii):
        self.num_radii = float(num_radii)
        
        print("    Set Number of Radii to", str(self.num_radii))
        
    def set_radius_step_arg(self, radius_step):
        self.radius_step = float(radius_step)
        
        print("    Set Radius Step to", str(self.radius_step))
    
    def set_debug_dot_detection_true(self):
        self.debug_dot_detection = True
        print("    Set Debug Dot Dotection to True")
        
    def set_syndrome_decoding_true(self):
        self.synd_decoding= True
        print("    Set Syndrome Decoding to True")
        
    def set_lampfish_decoding_true(self):
        self.lampfish_decoding = True
        print("    Set Lampfish Decoding to True")

    def set_lampfish_pixel_decoding_true(self):
        self.lampfish_pixel = True
        print("    Set Lampfish Pixel Decoding to True")
        
    def set_nuclei_radius_arg(self, nuclei_radius):
        self.nuclei_radius = float(nuclei_radius)
        
        print("    Set Nuclei Radius to", str(self.nuclei_radius))
        
    def set_flow_threshold_arg(self, flow_threshold):
        self.flow_threshold = float(flow_threshold)
        
        print("    Set Flow Probability Threshold to", str(self.nuclei_radius))
        
    def set_cell_prob_threshold_arg(self, cell_prob_threshold):
        self.cell_prob_threshold = float(cell_prob_threshold)
        
        print("    Set Cell Probabiliy Threshold to", str(self.cell_prob_threshold))
        
    def set_min_weight_adcg_arg(self, min_weight_adcg):
        self.min_weight_adcg = float(min_weight_adcg)
        
        print("    Set Min Weight ADCG to", str(self.min_weight_adcg))
        
    def set_final_improv_adcg_arg(self, final_improv_adcg):
        self.final_loss_adcg = float(final_improv_adcg)
        
        print("    Set Final Improvement ADCG to", str(self.final_loss_adcg))

    def set_nuclei_channel_arg(self, nuclei_arg):
        self.nuclei_channel_num = int(float(nuclei_arg))
        
        print("    Set Nuclei Channel Number to", str(self.nuclei_channel_num))
    #--------------------------------------------------------------------
    #Finished Setting Parameters
    
    def move_directory_contents(self, src, dest):
        """
        Basically just move files
        """
        os.makedirs(dest, exist_ok=True)
        src_with_asterisk = os.path.join(src, '*')
        os.system('cp ' + src_with_asterisk + ' ' + dest)
                
    
    
    #Set functions for analysis
    #--------------------------------------------------------------------
    def run_dot_detection(self):
        
        #print(f'{Dot_Detection=}')
        dot_detector = Dot_Detection(self.experiment_name, self.personal, self.position, self.locations_dir, 
                                               self.analysis_name, self.visualize_dots, self.normalization, self.background_subtraction, 
                                               self.decoding_individual, self.chromatic_abberration, self.dot_detection, self.gaussian_fitting, 
                                               self.strictness_dot_detection, self.dimensions, self.radial_center, self.num_zslices, 
                                               self.nbins, self.threshold, self.num_wav, self.num_z, 
                                               self.dot_radius, self.radius_step, self.num_radii, self.debug_dot_detection,
                                               self.min_weight_adcg, self.final_loss_adcg)
                                              
                                               
        timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                
        
        if self.dimensions == 2:
            
            locs_src = dot_detector.run_dot_detection_2d()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
            return locs_src
        
        
        locs_src = dot_detector.run_dot_detection()
        timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
        
        return locs_src
        
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
            #Get Number of Z slices
            #--------------------------------------------------------------------------------
            subdirs = os.listdir(self.data_dir)
            hyb_dirs = [sub_dir for sub_dir in subdirs if 'Hyb' in sub_dir]         
            assert len(hyb_dirs) > 0, "There are not HybCycle Directories in the experiment directory."
            hyb_dir = hyb_dirs[0]
            sample_tiff_src = os.path.join(self.data_dir, hyb_dir, self.position)
            sample_tiff = tiffy.load(sample_tiff_src, self.num_wav, self.num_z)
            num_zslices = sample_tiff.shape[0]
            #--------------------------------------------------------------------------------
            
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Segmentation')
            segmenter = Segmentation(self.data_dir, self.position, self.seg_dir, self.decoded_dir, self.locations_dir, self.barcode_dst, self.barcode_key_src, \
                        self.fake_barcodes, self.decoding_individual, self.num_zslices, self.segmentation, self.seg_data_dir, self.dimensions, num_zslices, \
                        self.labeled_img, self.edge_dist, self.dist_between_nuclei, self.bool_cyto_match, self.area_tol, self.cyto_channel_num, \
                        self.get_nuclei_seg, self.get_cyto_seg, self.num_wav, self.nuclei_radius, self.flow_threshold, self.cell_prob_threshold,
                        self.nuclei_channel_num)
        
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
            
            sample_tiff = tiffy.load(sample_tiff_src, self.num_wav, self.num_z)
            
            self.num_zslices = sample_tiff.shape[0]
        #--------------------------------------------------------------------------------
        
        
        print(f'{self.align=}')
        #Alignment
        #--------------------------------------------------------------------------------
        if self.align !=None or self.dot_detection != False or self.decoding_across == True or \
            self.decoding_individual != 'all':
                
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Alignment')
            if not self.decoding_with_previous_dots and not self.decoding_with_previous_locations:
                    
              
                    timer_tools.logg_elapsed_time(self.start_time, 'Starting Alignment')    
                    if self.align == None or self.align == 'fiducial_markers':
                        
     
                                           
                        offset = run_alignment.run_alignment(self.experiment_name, self.personal, self.position, 'no_align', self.num_wav, self.start_time)
                    
                    else:
                        
                        offset, align_errors = run_alignment.run_alignment(self.experiment_name, self.personal, self.position, self.align, self.num_wav, self.start_time)
                        offsets_path = os.path.join(path, 'offsets.json')
                        print("        Saving to", offsets_path, flush=True)
                        
                        align_errors_path = os.path.join(path, 'align_errors.json')
                        with open(align_errors_path, 'w') as jsonfile:
                            json.dump(align_errors, jsonfile)
                        
                    #Write Results to Path
                    #-----------------------------------------------------
                    offsets_path = os.path.join(path, 'offsets.json')
                    with open(offsets_path, 'w') as jsonfile:
                        json.dump(offset, jsonfile)
                    #-----------------------------------------------------
                    
                    #Get Visual Check for DAPI 
                    #-------------------------------------------------
                    dapi_check_dir = os.path.join(self.position_dir, 'Alignment_Checks')
                    os.makedirs(dapi_check_dir, exist_ok=True)
                    dapi_check_dst = os.path.join(dapi_check_dir, 'Aligned_and_Stacked_DAPI_S.tif')
                    get_stacked_dapi_s_align_check(offsets_path, dapi_check_dst, self.num_wav)
                    #-------------------------------------------------
                    
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
            self.locs_src = self.run_dot_detection()
        #--------------------------------------------------------------------------------
        
        #Run Fiducial Alignment 
        #--------------------------------------------------------------------------------
        if self.align == 'fiducial_markers':
            dst_fiducials_dir = os.path.join(self.position_dir, 'Alignment')
            try:
                os.mkdir(dst_fiducials_dir)
            except:
                pass
            
            fiducial_alignment.get_fiducial_offset(self.data_dir, self.position, dst_fiducials_dir, self.locs_src, self.num_wav)
        #--------------------------------------------------------------------------------
            
        #Declare Decoding Class if needed
        #--------------------------------------------------------------------------------
        if self.decoding_across == True or self.decoding_individual != 'all' \
        or self.decoding_with_previous_dots == True or self.decoding_with_previous_locations == True or self.decoding_non_barcoded == True \
        or self.lampfish_decoding:
            
            self.move_directory_contents(self.barcode_key_src, self.barcode_dst)
            
            self.barcode_key_src = self.barcode_dst
            
            decoder = Decoding(self.data_dir, self.position, self.decoded_dir, self.locations_dir, self.position_dir, self.barcode_dst, \
                self.barcode_key_src, self.decoding_with_previous_dots, self.decoding_with_previous_locations, self.fake_barcodes, \
                self.decoding_individual, self.min_seeds, self.allowed_diff, self.dimensions, self.num_zslices, self.segmentation, \
                self.decode_only_cells, self.labeled_img, self.num_wav, self.synd_decoding, self.lampfish_pixel, self.start_time)
        #--------------------------------------------------------------------------------
        
        
        if self.lampfish_decoding == True:
            if self.dot_detection == False:
                timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                self.run_dot_detection()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
            
            timer_tools.logg_elapsed_time(self.start_time, 'Starting LampFISH Decoding')
            decoder.run_lampfish_decoding()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending LampFISH Decoding')  
            
        if self.synd_decoding == True:
            #Run Decoding Individual
            #--------------------------------------------------------------------------------
            if not self.decoding_individual == 'all':
                if self.dot_detection == False:
                    timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                    self.run_dot_detection()
                    timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
                    
                timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding Individual')
                decoder.run_synd_decoding_individual()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding Individual')
            #--------------------------------------------------------------------------------
        else:
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
                decoder.run_decoding_individual()
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
                decoder.run_decoding_across()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding Across')
                
            if self.decoding_non_barcoded== True:
                if self.dot_detection == False:
                    timer_tools.logg_elapsed_time(self.start_time, 'Starting Dot Detection')
                    self.run_dot_detection()
                    timer_tools.logg_elapsed_time(self.start_time, 'Ending Dot Detection')
                
                timer_tools.logg_elapsed_time(self.start_time, 'Starting Decoding Non-Barcoded')
                decoder.run_non_barcoded_decoding()
                timer_tools.logg_elapsed_time(self.start_time, 'Ending Decoding Non-Barcoded')
                    
            #--------------------------------------------------------------------------------
            
        
        #Declare Segmentation
        #--------------------------------------------------------------------------------
        if self.segmentation != False:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting Segmentation')
            segmenter = Segmentation(self.data_dir, self.position, self.seg_dir, self.decoded_dir, self.locations_dir, self.barcode_dst, self.barcode_key_src, \
                self.fake_barcodes, self.decoding_individual, self.num_zslices, self.segmentation, self.seg_data_dir, self.dimensions, self.num_zslices, \
                self.labeled_img, self.edge_dist, self.dist_between_nuclei, self.bool_cyto_match, self.area_tol, self.cyto_channel_num, \
                self.get_nuclei_seg, self.get_cyto_seg, self.num_wav, self.nuclei_radius, self.flow_threshold, self.cell_prob_threshold, 
                self.nuclei_channel_num)
                
            print(f'{self.labeled_img.shape=}')
            if self.decoding_across == True or \
                self.decoding_with_previous_dots == True or \
                self.decoding_with_previous_locations == True:
                
                segmenter.run_segmentation_across()      

            elif not self.decoding_individual == 'all':
                
                print(f'{self.labeled_img.shape=}')
                print('Running Segmentation Individual')
                segmenter.run_segmentation_individually()
            
            elif self.decoding_non_barcoded == True:
                
                segmenter.run_segmentation_non_barcoded()
            
            timer_tools.logg_elapsed_time(self.start_time, 'Ending Segmentation')
        #--------------------------------------------------------------------------------
    
        
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
            elif self.decoding_individual!='all':
                post_analysis.run_on_off_barcode_analysis_indiv()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending  On Off Barcode Plot Analysis')
        #--------------------------------------------------------------------------------
    
    
        #Run False Positive Rate Analysis    
        #--------------------------------------------------------------------------------
        if self.segmentation != False and self.false_positive_rate_analysis == True:
            timer_tools.logg_elapsed_time(self.start_time, 'Starting False Positive Rate')
            if self.decoding_across ==True:
                post_analysis.run_false_positive_rate_analysis_across()
            elif self.decoding_individual!='all':
                post_analysis.run_false_positive_rate_analysis_indiv()
            timer_tools.logg_elapsed_time(self.start_time, 'Ending False Positive Rate')
        #--------------------------------------------------------------------------------
        
        #Label analysis as finished 
        #--------------------------------------------------------------------------------
        timer_tools.logg_elapsed_time(self.start_time, 'Finished with Analysis of Position')
        #--------------------------------------------------------------------------------
        
        
        #Send email for finished analysis
        #--------------------------------------------------------------------------------
        print(f'{self.email=}')
        if self.email != 'none':
            send_finished_notif(self.analysis_dir, self.email)
        #--------------------------------------------------------------------------------
            
        #Check if all positions are finished
        #--------------------------------------------------------------------------------
        if are_logs_finished(self.analysis_dir):
            
            #Combine all dots
            if self.dot_detection != False:
                combine_locs_csv_s(self.analysis_dir)
            
            #Combine all decoded genes
            if not self.decoding_individual == 'all':
                for channel in self.decoding_individual:
                    combine_pos_genes(self.analysis_dir, channel)
                
                #Get pearson correlation of positions
                get_correlated_positions
        #--------------------------------------------------------------------------------
                    
        #Send Analysis to onedrive    
        send_analysis_to_onedrive(self.analysis_dir)

    #--------------------------------------------------------------------------------
    #End of running the parameters
            
        
        
