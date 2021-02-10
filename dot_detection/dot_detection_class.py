import os
import json
import sys
import scipy.io as sio
from scipy.io import loadmat
import numpy as np
import glob
import pandas as pd
from scipy.ndimage._ni_support import _normalize_sequence
import scipy.ndimage as ndi
import cv2
import warnings
import json
import warnings
import pickle
import multiprocessing
import subprocess
import time
import shutil



#Import some helpers
#--------------------------------------------------------------------------------
from load_tiff import tiffy
from dot_detection.visualize_dots.tiff_visuals import plot_and_save_locations
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.dot_detectors_2d.dot_detector_2d import find_dots
from dot_detection.helpers.multiprocessed_points import combine_multiprocessed_points
from dot_detection.rand_list import are_jobs_finished, get_random_list
from dot_detection.helpers.combine_multi_dots import combine_locs
#--------------------------------------------------------------------------------



if os.environ.get('DATA_PIPELINE_MAIN_DIR') is not None:
    main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']
else:
    raise Exception("The Main Directory env variable is not set. Set DATA_PIPELINE_MAIN_DIR!!!!!!!!")


#Dot Detection class for setting dot detection
#=====================================================================================
class Dot_Detection:
    def __init__(self, experiment_name, personal, position, locations_dir, \
                   analysis_name, visualize_dots, normalization, \
                   background_subtraction, decoding_individual, chromatic_abberration, \
                   dot_detection, gaussian_fitting, strictness_dot_detection, dimensions, \
                   radial_center, num_zslices, nbins, threshold):

        self.experiment_name = experiment_name
        self.personal = personal
        self.position = position 
        self.locations_dir = locations_dir
        self.analysis_name = analysis_name
        self.visualize_dots = visualize_dots
        self.normalization = normalization
        self.background_subtraction = background_subtraction
        self.decoding_individual = decoding_individual
        self.chromatic_abberration = chromatic_abberration
        self.dot_detection = dot_detection
        self.gaussian_fitting = gaussian_fitting
        self.strictness_dot_detection = strictness_dot_detection
        self.dimensions = dimensions
        self.radial_center = radial_center
        self.num_zslices = num_zslices
        self.nbins = nbins
        self.threshold = threshold
        
        #Set Directories
        #--------------------------------------------------------------
        self.analysis_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, self.analysis_name)
        self.position_dir = os.path.join(self.analysis_dir, self.position.split('.ome')[0])
        self.logging_pos = os.path.join(self.position_dir, 'logging.logs')
        self.decoded_dir = os.path.join(self.position_dir, 'Decoded')
        self.locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
        #--------------------------------------------------------------
        
    def save_locs_shape(self, locations_src):
        points = loadmat(locations_src)['points']
        dst = os.path.join(os.path.dirname(locations_src), \
                           os.path.basename(locations_src).replace('.mat', '') + '_Shape.txt')
    
        with open(dst, "w") as f:
            for i in range(points.shape[0]):
                f.write('Channel ' + str(i) + ' Number of Dots: ' + str(points[i][0].shape[0]) + '\n')
    
 
    def run_dot_detection_2d(self):
        
        for z in range(self.num_zslices):
            
            #Run Dot Detection
            #--------------------------------------------------------------------
            points, intensities = self.get_dot_locations()
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
            
    
            sio.savemat(locations_path,{'points': points, 'intensity': intensities}, oned_as = 'column')
            self.save_locs_shape(locations_path)
            #--------------------------------------------------------------------

    def run_dot_detection(self):
        
        if self.dimensions == 2:
            self.run_dot_detection_2d()
            return None
            
        print("    Getting Dot Locations with", self.dot_detection, flush=True)
        
        #Run Dot Detection
        #--------------------------------------------------------------------
            
        points, intensities = self.get_dot_locations()

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
        

        sio.savemat(locations_path,{'points': points, 'intensity': intensities}, oned_as = 'column')
        self.save_locs_shape(locations_path)
        #--------------------------------------------------------------------
        
    def get_dot_locations(self, z_slice= 'all'):

        #Setting Proper Directories
        #-----------------------------------------------------------------
        exp_dir = os.path.join('/groups/CaiLab/personal', self.personal, 'raw', self.experiment_name)
        
        sub_dirs = get_and_sort_hybs(os.path.join(exp_dir,'*'))
        
        offsets_src = os.path.join(self.position_dir, 'offsets.json')
        #-----------------------------------------------------------------                   
                        
    
        #Open offsets
        #-----------------------------------------------------------------
        with open(offsets_src) as json_file: 
            offsets = json.load(json_file)
        #-----------------------------------------------------------------    
        
        
        #Check for first tiff
        #-----------------------------------------------------------------
        check_if_first_tiff = 0 
        #-----------------------------------------------------------------
        
        #Get Random List    
        #-------------------------------------------------------------------
        rand_list = get_random_list(len(sub_dirs))
        #-------------------------------------------------------------------
        
        #Get CWD
        #-------------------------------------------------------------------
        cwd = os.getcwd()
        dot_detection_dir = os.path.join(cwd, 'dot_detection', 'dot_detectors_3d')
        #-------------------------------------------------------------------

        #Run alignment
        #-----------------------------------------------------------------
        print(f'{sub_dirs=}')
        for sub_dir in sub_dirs:
            
            if "Hyb" in sub_dir:
            
                #Get Exact offset needed
                #------------------------------------------------
                tiff_file_path = os.path.join(sub_dir, self.position)
                
                split_up = tiff_file_path.split(os.sep)
                key = os.path.join(split_up[-2], split_up[-1])
                
                offset = offsets[key]
                if len(offset) == 2:
                    offset.append(None)
                #------------------------------------------------
                
                #Print Statement
                #------------------------------------------------
                hyb = os.path.split(sub_dir)[1] 
                print("    Running dot detection on", hyb, 'for', self.position, flush=True)
                #------------------------------------------------
                
                #Set results dir
                #------------------------------------------------
                temp_dir = os.path.join(main_dir, 'personal', 'nrezaee', 'temp_dots')
                rand = rand_list[sub_dirs.index(sub_dir)]
                rand_dir = os.path.join(temp_dir, rand)
                os.mkdir(rand_dir)
                #------------------------------------------------
             
                if 'top' in self.dot_detection:
                    
                    n_dots = int(self.dot_detection.split('top')[1].split('dots')[0])
                    
                    list_cmd = ['python', dot_detection_dir+ '/get_top_n_dots.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], '--analysis_name', self.analysis_name, \
                            '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--n_dots', n_dots, '--rand', rand_dir]
                    
                    list_cmd = [str(i) for i in list_cmd]
               
                elif self.dot_detection == "biggest jump":
                    

                    list_cmd = ['python', dot_detection_dir+ '/hist_jump.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--z_slices', z_slice]
                    
                    list_cmd = [str(i) for i in list_cmd]
                
                elif self.dot_detection == "matlab 3d":
                    

                    list_cmd = ['python', dot_detection_dir + '/matlab_3d.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--z_slices', z_slice, '--nbins',  \
                            self.nbins, '--threshold', self.threshold]
                    
                    list_cmd = [str(i) for i in list_cmd]
                
                else:
                    
                    raise Exception("The dot detection argument was not valid.")    
                
                
                #Call Sbatch
                #------------------------------------------------
                cmd = ' '.join(list_cmd)

                #print(f'{cmd=}')
                script_name = os.path.join(rand_dir, 'dot_detection.sh')
                with open(script_name , 'w') as f:
                    print('#!/bin/bash', file=f) 
                    print(cmd, file=f)  
                
                #os.system(cmd)
                out_path = os.path.join(rand_dir, 'slurm.out')
                call_me = ['sbatch', '--job-name', rand_list[sub_dirs.index(sub_dir)], '--output', out_path, "--time", "0:10:00", "--mem-per-cpu", "5G", '--ntasks', '1', script_name]
                print(" ".join(call_me))
                subprocess.call(call_me)
                #------------------------------------------------
                
                
        while not are_jobs_finished(rand_list):
            print("Waiting for Dot Detection Jobs to Finish")
            time.sleep(2)
        

        locations = np.array(combine_locs(rand_list))
        
        #Delete the rand dirs
        #----------------------------------------------
        # for rand in rand_list:
        #     rand_dir = os.path.join(temp_dir, rand)
        #     shutil.rmtree(rand_dir)
        #----------------------------------------------
        
        points = locations[:,0]
        intensities = locations[:,1]
        
        return points, intensities
        
        
            
            
                