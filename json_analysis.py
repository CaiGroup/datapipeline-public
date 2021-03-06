"""
This script is where the magic happens. It loads the json file and 
uses the parameters in the json file to set parameters for the analysis

After this script is done setting the parameters it runs the analysis with
the parameters. It uses analysis_class.py heavily to do this.
"""

import os 
import json 
import argparse
import shutil
import sys
import math


main_dir = '/groups/CaiLab'

#Import Analysis Class
#----------------------------------------------------------
from datapipeline.analysis_class import Analysis
#----------------------------------------------------------

#Set Arguments
#----------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--json", help="json for analysis")
parser.add_argument("--position", help="position to be processed")
parser.add_argument("--personal", help="personal directory")
parser.add_argument("--experiment_name", help="experiment name")
parser.add_argument("--slurm", help="Determine script is run on slurm to direct output to file in analyses/")
parser.add_argument("--email", help="Determine script is run on slurm to direct output to file in analyses/")
args = parser.parse_args()
#----------------------------------------------------------


#Runs analysis by setting parameters for Analysis Class
#=========================================================================
def run_analysis(json_name, position):
    """
    Run a json file with a specific position
    
    This file makes an Analysis Object from the analysis_class.py file
    """
    
    
    #Get Json Path
    #----------------------------------------------------------
    analysis_name = json_name.split('.json')[0]

    json_path = os.path.join(main_dir, 'analyses', args.personal, args.experiment_name, \
                            analysis_name, json_name)
    
    print("Json Path:", json_path)
    #----------------------------------------------------------
    
    
    #Open json
    #----------------------------------------------------------
    with open(json_path) as json_file: 
        non_lowercase_data = json.load(json_file) 
        
    data = {}
    for key, value in non_lowercase_data.items():
        if type(value) == str:
            
            if key.lower() == 'personal' or key.lower() == 'experiment_name':

                data[key.lower()] = value
                
            else:
            
                data[key.lower()] = value.lower()
            
        else:
            data[key.lower()] = value

    print("Parameters set:", data)
    #----------------------------------------------------------


    #Output print statements to file if running slurm
    #----------------------------------------------------------
    if args.slurm == 'True':
    
        #Change print output to file    
        #----------------------------------------------------------
        orig_stdout = sys.stdout
        
        output_dir = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'],
                                   analysis_name, position.split('.ome')[0], 'Output')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_file = os.path.join(output_dir, 'output.txt')
                                   
        print("Print statements outputted to", output_file)
        
        redirected_output = open(output_file, 'w')
        
        sys.stdout = redirected_output
        #----------------------------------------------------------
    #----------------------------------------------------------


    #Declare Analysis Class
    #---------------------------------------------------------
    analysis = Analysis(experiment_name=data['experiment_name'],
                analysis_name=json_name.split('.json')[0],
                personal = data['personal'],
                position = args.position, 
                email = args.email)
    #----------------------------------------------------------
    

    #Alignment
    #----------------------------------------------------------
    if 'alignment' in data.keys():
        if not data['alignment'] == 'none':
            print(f"{data['alignment']=}", flush=True)
            analysis.set_alignment_arg(data['alignment'])
    #----------------------------------------------------------
    
    
    #Align Errors
    #----------------------------------------------------------
    if 'alignment errors' in data.keys():
        if data['alignment errors'] == 'true':
            analysis.set_align_errors_true()
    #----------------------------------------------------------   
    

    
    #background subtraction
    #----------------------------------------------------------
    if 'background subtraction' in data.keys():
        if data['background subtraction'] == 'true':
            analysis.set_background_subtraction_true()
    #----------------------------------------------------------  
   
   
    #Chromatic Abberration
    #----------------------------------------------------------
    if 'chromatic aberration' in data.keys():
        if data['chromatic aberration'] == 'true':
            analysis.set_chromatic_aberration_true()
    #----------------------------------------------------------
    
    
    #Normalization
    #----------------------------------------------------------
    if 'normalization' in data.keys():
        if data['normalization'] == 'true':
            analysis.set_normalization_true()
    #----------------------------------------------------------
    

    #Deconvolution
    #----------------------------------------------------------
    if 'deconvolution' in data.keys():
        if data['deconvolution'] == 'true':
            analysis.set_deconvolution_true()
    #----------------------------------------------------------
    
    
    #Dot Detection
    #----------------------------------------------------------
    if 'dot detection' in data.keys():
        if data['dot detection'] != 'none':
            analysis.set_dot_detection_arg(data['dot detection'])   
    #----------------------------------------------------------     


    #Decoding
    #----------------------------------------------------------
    if 'decoding' in data.keys():
        if 'across' in data['decoding']:
            analysis.set_decoding_across_true()   
        elif 'none' in data['decoding']:
            pass
        elif 'non barcoded'== data['decoding']:
            analysis.set_non_barcoded_decoding_true()
        elif 'individual' in data['decoding'].keys(): 
            analysis.set_decoding_individual(data['decoding']['individual'])
    #----------------------------------------------------------  
    
    
    #Visualize Dots
    #----------------------------------------------------------
    if 'visualize dot detection' in data.keys():
        if data['visualize dot detection'] == 'true':
            analysis.set_visual_dot_detection_true()
    #----------------------------------------------------------
    
    
    #Colocalize
    #----------------------------------------------------------
    if 'colocalize' in data.keys():
        if data['colocalize'] == 'true':
            analysis.set_colocalize_true()   
    #----------------------------------------------------------  
 
    #Decoding with Previous
    #----------------------------------------------------------
    if 'decoding with previous points variable' in data.keys():
        if data['decoding with previous points variable'] == 'true':
            analysis.set_decoding_with_previous_dots_true()   
    #----------------------------------------------------------  
    
    #Decoding with Previous Locations
    #----------------------------------------------------------
    if 'decoding with previous locations variable' in data.keys():
        if data['decoding with previous locations variable'] == 'true':
            analysis.set_decoding_with_previous_locations_true()   
    #----------------------------------------------------------  
    
    #Segmentation
    #----------------------------------------------------------
    if 'segmentation' in data.keys():
        print(f'{data["segmentation"]=}')
        if not data['segmentation'] == 'no':
            analysis.set_segmentation_arg(data['segmentation'])
    #----------------------------------------------------------   
    
    #Add Fake Barcodes
    #----------------------------------------------------------
    if 'add fake barcodes' in data.keys():
        if data['add fake barcodes'] == 'true':
            analysis.set_fake_barcodes_true()
    #----------------------------------------------------------   
    
    #Generate Analysis of Segmentation
    #----------------------------------------------------------
    if 'on/off barcode analysis' in data.keys():
        if data['on/off barcode analysis'] == 'true':
            analysis.set_on_off_barcode_analysis_true()
    #----------------------------------------------------------   
    
    #Generate Analysis of Segmentation
    #----------------------------------------------------------
    if 'false positive rate analysis' in data.keys():
        if data['false positive rate analysis'] == 'true':
            analysis.set_false_positive_rate_analysis_true()
    #----------------------------------------------------------
    
    #Generate Analysis of Segmentation
    #----------------------------------------------------------
    if 'gaussian fitting' in data.keys():
        if data['gaussian fitting'] == 'true':
            analysis.set_gaussian_fitting_true()
    #----------------------------------------------------------
    

    #Generate Analysis of Segmentation
    #----------------------------------------------------------
    if 'radial center' in data.keys():
        if data['radial center'] == 'true':
            analysis.set_radial_center_true()
    #----------------------------------------------------------
    
    #Set Allowed Diff
    #----------------------------------------------------------
    if 'allowed_diff' in data.keys():
        if not data['allowed_diff'] == 'none':
            analysis.set_allowed_diff_arg(data['allowed_diff'])
    #----------------------------------------------------------
    
    #Set Dot Detection Strictness
    #----------------------------------------------------
    if 'strictness' in data.keys():
        if not data['strictness'] == 'none':
            analysis.set_strictness_arg(data['strictness'])
    #----------------------------------------------------------
    
    #Set Min Seeds
    #----------------------------------------------------
    if 'min seeds' in data.keys():
        if not data['min seeds'] == 'none':
            analysis.set_min_seeds_arg(data['min seeds'])
    #----------------------------------------------------------
    
    #Set Hamming Distance Analysis
    #----------------------------------------------------
    if 'hamming analysis' in data.keys():
        if data['hamming analysis'] == 'true':
            analysis.set_hamming_analysis_true()
    #----------------------------------------------------------
    
    
    #Set All Post Analyses
    #----------------------------------------------------
    if 'all post analyses' in data.keys():
        if data['all post analyses'] == 'true':
            analysis.set_all_post_analyses_true()
    #----------------------------------------------------------
    
    #Set Distance Between Nuclei
    #----------------------------------------------------
    if 'distance between nuclei' in data.keys():
        if data['distance between nuclei'] != 'none':
            analysis.set_dist_between_nuclei_arg(data['distance between nuclei'])
    #----------------------------------------------------------
    
    #Set Distance Between Nuclei
    #----------------------------------------------------
    if 'edge deletion' in data.keys():
        if data['edge deletion'] != 'none':
            analysis.set_edge_deletion_arg(data['edge deletion'])
    #----------------------------------------------------------

    #Set Edges to Delete
    #----------------------------------------------------
    if 'nuclei cyto match' in data.keys():
        if data['nuclei cyto match'] == 'true':
             analysis.set_nuclei_cyto_match_true()
    #----------------------------------------------------------
    
    
    #Only Decode Dots in Cells
    #----------------------------------------------------
    if 'only decode dots in cells' in data.keys():
        if data['only decode dots in cells'] == 'true':
            analysis.set_decode_only_cells_true()
    #----------------------------------------------------------

    #Set Nbins for dote detection
    #----------------------------------------------------
    if 'nbins' in data.keys():
        if data['nbins'] != 'none':
            analysis.set_nbins_arg(data['nbins'])
    #----------------------------------------------------------
    
    #Set Nbins for dote detection
    #----------------------------------------------------
    if 'threshold' in data.keys():
        if data['threshold'] != 'none':
            analysis.set_threshold_arg(data['threshold'])
    #----------------------------------------------------------
    
    #Set Cyto Channel Number
    #----------------------------------------------------
    if 'cyto channel number' in data.keys():
        if data['cyto channel number'] != 'none':
            analysis.set_cyto_channel_arg(data['cyto channel number'])
    #----------------------------------------------------------

    #Set Nuclei Labeled Image
    #----------------------------------------------------
    if 'nuclei labeled image' in data.keys():
        if data['nuclei labeled image'] == 'true':
             analysis.set_nuclei_labeled_img_true()
    #----------------------------------------------------------
    
    #Set Cyto Labeled Image
    #----------------------------------------------------
    if 'cyto labeled image' in data.keys():
        if data['cyto labeled image'] == 'true':
             analysis.set_cyto_labeled_img_true()
    #----------------------------------------------------------
    
    #Matching Tolerance for Segmentation
    #----------------------------------------------------
    if 'area_tol' in data.keys():
        if data['area_tol'] != 'none':
            analysis.set_area_tol_arg(data['area_tol'])
    #----------------------------------------------------------
    
    #Set Min Seeds
    #----------------------------------------------------
    if 'num of wavelengths' in data.keys():
        if not data['num of wavelengths'] == 'none':
            analysis.set_num_wavelengths_arg(data['num of wavelengths'])
    #----------------------------------------------------------
    
    #Set Dimensions
    #----------------------------------------------------
    if 'dimensions' in data.keys():
        if not data['dimensions'] == 'none':
            analysis.set_dimensions_arg(data['dimensions'])
    #----------------------------------------------------------

    #Set Number Of Z
    #----------------------------------------------------
    if 'z slices' in data.keys():
        if not data['z slices'] == 'none':
            analysis.set_z_slices_arg(data['z slices'])
    #----------------------------------------------------------
    
    #Set Dot Radius
    #----------------------------------------------------
    if 'dot radius' in data.keys():
        if not data['dot radius'] == 'none':
            analysis.set_dot_radius_arg(data['dot radius'])
    #----------------------------------------------------------
    
    #Set Overlap
    #----------------------------------------------------
    if 'overlap' in data.keys():
        if not data['overlap'] == 'none':
            analysis.set_dot_overlap_arg(data['overlap'])
    #----------------------------------------------------------
    
    #Num of Radii
    #----------------------------------------------------
    if 'num of radii' in data.keys():
        if not data['num of radii'] == 'none':
            analysis.set_num_radii_arg(data['num of radii'])
    #----------------------------------------------------------

    #Radius Step
    #----------------------------------------------------
    if 'radius step' in data.keys():
        if not data['radius step'] == 'none':
            analysis.set_radius_step_arg(data['radius step'])
    #----------------------------------------------------------
    
    
    #Debug Dot Detection
    #----------------------------------------------------
    if 'debug dot detection' in data.keys():
        if data['debug dot detection'] == 'true':
            analysis.set_debug_dot_detection_true()
    #----------------------------------------------------------    

    #Cellpose Radius
    #----------------------------------------------------
    if 'nuclei radius' in data.keys():
        if data['nuclei radius'] != 'none':
            analysis.set_nuclei_radius_arg(data['nuclei radius'])
    #----------------------------------------------------------
    
    #Cellpose Cell Prob Threshold
    #----------------------------------------------------
    if 'cell prob threshold' in data.keys():
        if data['cell prob threshold'] != 'none':
            analysis.set_cell_prob_threshold_arg(data['cell prob threshold'])
    #----------------------------------------------------------
    
    #Cellpose Flow Threshold
    #----------------------------------------------------
    if 'flow threshold' in data.keys():
        if data['flow threshold'] != 'none':
            analysis.set_flow_threshold_arg(data['flow threshold'])
    #----------------------------------------------------------
    
    #Set Nuclei Channel Number
    #----------------------------------------------------
    if 'nuclei channel number' in data.keys():
        if data['nuclei channel number'] != 'none':
            analysis.set_nuclei_channel_arg(data['nuclei channel number'])
    #----------------------------------------------------------
    
    #Cyto Cellpose Flow Threshold
    #----------------------------------------------------
    if 'cyto flow threshold' in data.keys():
        if data['cyto flow threshold'] != 'none':
            analysis.set_cyto_flow_threshold_arg(data['cyto flow threshold'])
    #----------------------------------------------------------
    
    #Cyto Cellpose Prob Threshold
    #----------------------------------------------------
    if 'cyto cell prob threshold' in data.keys():
        if data['cyto cell prob threshold'] != 'none':
            analysis.set_cyto_cell_prob_threshold_arg(data['cyto cell prob threshold'])
    #----------------------------------------------------------
    
    #Cyto Radius
    #----------------------------------------------------
    if 'cyto radius' in data.keys():
        if data['cyto radius'] != 'none':
            analysis.set_cyto_radius_arg(data['cyto radius'])
    #----------------------------------------------------------
    
    #Stack z slices
    #----------------------------------------------------------
    if 'stack z slices in dot detection' in data.keys():
        if data['stack z slices in dot detection'] != 'none':
            analysis.set_stack_z_slices_in_dot_detection_true()
    #----------------------------------------------------------
    
    #Background Blob Removal
    #----------------------------------------------------------
    if 'background blob removal' in data.keys():
        if data['background blob removal'] != 'none':
            analysis.set_background_blob_removal_true()
    #----------------------------------------------------------
    
    #Tophat Preprocessing
    #----------------------------------------------------------
    if 'tophat preprocessing' in data.keys():
        if data['tophat preprocessing'] != 'none':
            analysis.set_tophat_true()
    #----------------------------------------------------------

    #Tophat Preprocessing
    #----------------------------------------------------------
    if 'tophat raw data preprocessing' in data.keys():
        if data['tophat raw data preprocessing'] != 'none':
            analysis.set_tophat_raw_data_true()
    #----------------------------------------------------------
    
    #Rolling ball background subtraction
    #----------------------------------------------------------
    if 'rolling ball preprocessing' in data.keys():
        if data['rolling ball preprocessing'] != 'none':
            analysis.set_rolling_ball_true()
    #----------------------------------------------------------

    #Blur Preprocessing
    #----------------------------------------------------------
    if 'blur preprocessing' in data.keys():
        if data['blur preprocessing'] != 'none':
            analysis.set_blur_preprocessing_true()
    #----------------------------------------------------------
    
    #Blur Kernel Size
    #----------------------------------------------------------
    if 'blur kernel size' in data.keys():
        if data['blur kernel size'] != 'none':
            analysis.set_blur_preprocessing_kernel_size_arg(data['blur kernel size'])
    #----------------------------------------------------------
    
    #Rolling Ball size
    #----------------------------------------------------------
    if 'blur back kernel size' in data.keys():
        if data['blur back kernel size'] != 'none':
            analysis.set_blur_back_sub_kernel_size_arg(data['blur back kernel size'])
    #----------------------------------------------------------
    
    #Tophat Ball size
    #----------------------------------------------------------
    if 'tophat kernel size' in data.keys():
        if data['tophat kernel size'] != 'none':
            analysis.set_tophat_kernel_size_arg(data['tophat kernel size'])
    #----------------------------------------------------------

    #Tophat Ball size
    #----------------------------------------------------------
    if 'tophat raw data kernel size' in data.keys():
        if data['tophat raw data kernel size'] != 'none':
            analysis.set_tophat_raw_data_kernel_size_arg(data['tophat raw data kernel size'])
    #----------------------------------------------------------
    
    #Set Min Sigma
    #----------------------------------------------------
    if 'min sigma dot detection' in data.keys():
        if not data['min sigma dot detection'] == 'none':
            analysis.set_min_sigma_arg(data['min sigma dot detection'])
    #----------------------------------------------------------
    
    #Set Max Sigma
    #----------------------------------------------------
    if 'max sigma dot detection' in data.keys():
        if not data['max sigma dot detection'] == 'none':
            analysis.set_max_sigma_arg(data['max sigma dot detection'])
    #----------------------------------------------------------
    
    #Set Num Sigma
    #----------------------------------------------------
    if 'num sigma dot detection' in data.keys():
        if not data['num sigma dot detection'] == 'none':
            analysis.set_num_sigma_arg(data['num sigma dot detection'])
    #----------------------------------------------------------

    #Set Remove Extremely Bright dots
    #----------------------------------------------------
    if 'remove very bright dots' in data.keys():
        if not data['remove very bright dots'] == 'none':
            analysis.set_remove_very_bright_dots_arg(data['remove very bright dots'])
    #----------------------------------------------------------
    
    #Set Dilate Background Kernel
    #----------------------------------------------------
    if 'dilate background kernel' in data.keys():
        if not data['dilate background kernel'] == 'none':
            analysis.set_dilate_background_kernel_arg(data['dilate background kernel'])
    #----------------------------------------------------------
    
    #Writ
    #----------------------------------------------------------
    analyses_dir = os.path.join(main_dir, 'analyses', args.personal, args.experiment_name, analysis_name)
    
    position_dir = os.path.join(analyses_dir, args.position.split('.ome')[0])

    # This call actually runs all of the steps given the parameters we've set up:
    analysis.write_results(position_dir)
    #----------------------------------------------------------
    
    if args.slurm == 'True':
        
        #Change output back to normal
        #----------------------------------------------------------
        sys.stdout = orig_stdout
        redirected_output.close()
        #----------------------------------------------------------
        
    return None
#=========================================================================    

if __name__ == '__main__':
    run_analysis(args.json, args.position)
