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
from analysis_class import Analysis
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
        
        output_dir = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'], \
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
    analysis = Analysis(experiment_name=data['experiment_name'], \
                analysis_name=json_name.split('.json')[0], \
                personal = data['personal'], \
                position = args.position, 
                email = args.email)
    #----------------------------------------------------------
    

    #Alignment
    #----------------------------------------------------------
    if 'alignment' in data.keys():
        if not data['alignment'] == 'none':
            hi = 'hello'
            print('---------------------------------', flush = True)
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
            analysis.set_chromatic_abberration_true()
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
    
    #Writ
    #----------------------------------------------------------
    analyses_dir = os.path.join(main_dir, 'analyses', args.personal, args.experiment_name, analysis_name)
    
    position_dir = os.path.join(analyses_dir, args.position.split('.ome')[0])
    
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
    
    
run_analysis(args.json, args.position)
    
        
    
    
    
        
        
    
        
        
    