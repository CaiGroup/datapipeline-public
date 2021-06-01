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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sys.path.insert(0, os.getcwd())


#Import some helpers
#--------------------------------------------------------------------------------
from load_tiff import tiffy
from dot_detection.reorder_hybs import get_and_sort_hybs
from dot_detection.dot_detectors_2d.dot_detector_2d import find_dots
from dot_detection.helpers.multiprocessed_points import combine_multiprocessed_points
from dot_detection.rand_list import are_jobs_finished, get_random_list
from dot_detection.helpers.combine_multi_dots import combine_locs
from timer import timer_tools
#--------------------------------------------------------------------------------



main_dir = '/groups/CaiLab'
#Dot Detection class for setting dot detection
#=====================================================================================
class Dot_Detection:
    def __init__(self, experiment_name, personal, position, locations_dir, 
                   analysis_name, visualize_dots, normalization, background_subtraction,
                   decoding_individual, chromatic_abberration, dot_detection, gaussian_fitting, 
                   strictness_dot_detection, dimensions, radial_center, num_zslices, 
                   nbins, threshold, num_wav, z_slices, 
                   dot_radius, radius_step, num_radii, debug_dot_detection,
                   min_weight_adcg, final_loss_adcg, test1, test2):

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
        self.num_wav = num_wav
        self.num_z = z_slices
        self.nbins = float(nbins)
        self.dot_radius = dot_radius
        self.radius_step = radius_step
        self.num_radii = num_radii
        self.debug_dot_detection = debug_dot_detection
        self.min_weight_adcg = min_weight_adcg
        self.final_loss_adcg = final_loss_adcg
        
        
        #Set Directories
        #--------------------------------------------------------------
        self.analysis_dir = os.path.join(main_dir, 'analyses', self.personal, self.experiment_name, self.analysis_name)
        self.position_dir = os.path.join(self.analysis_dir, self.position.split('.ome')[0])
        self.logging_pos = os.path.join(self.position_dir, 'logging.logs')
        self.decoded_dir = os.path.join(self.position_dir, 'Decoded')
        self.locations_dir = os.path.join(self.position_dir, 'Dot_Locations')
        #--------------------------------------------------------------
        
    def get_z_slices_check_img(self, df,dst_dir):
        z_s = np.array(np.round(df.z))+1
        plt.figure()
        plt.title("Number of Dots Across Z's", fontsize=20)
        plt.xlabel("Z Slice")
        plt.ylabel("Number of Dots")
        plt.xticks(list(set(z_s)))
        plt.hist(z_s)
        plt.savefig(os.path.join(dst_dir, 'Dots_Across_Z_Slices.png'))
        
    def get_heatmap_of_xy(self, df, dst_dir):
        size = int(np.round(df[['x','y']].values.max()))
        tiles_across = 16
        print(f'{size=}')
        heatmap_sections = []
        step_size = int(np.round(size/tiles_across))
        for x in range(0,size,step_size):
            heatmap_slide = []
            for y in range(0,size,step_size):
                df_square = df[(df.x >= x) & (df.x <=(x+512)) & \
                               (df.y >=y) & (df.y <=(y+512))]
    
                heatmap_slide.append(df_square.shape[0])
    
            heatmap_sections.append(heatmap_slide)
        heatmap_sections.reverse()
    
        heatmap_sections = np.array(heatmap_sections)
        heatmap_sections = np.rot90(heatmap_sections,2).T
    
        colormap = sns.color_palette("Greens")
        plt.figure()
        plt.title('Map of Locations Across X and Y', fontsize=15)
        map_xy = sns.heatmap(heatmap_sections, cmap=colormap)
        map_xy.set_xticklabels(list(range(0,size,step_size)), fontsize = 5)
        map_xy.set_yticklabels(list(range(0,size,step_size)), fontsize = 5)
        
        plt.savefig(os.path.join(dst_dir, 'Map_of_XY_Locations.png'))
    
    def get_location_checks(self, locations_csv_src):
        dst_dir = os.path.join(os.path.dirname(locations_csv_src), 'Location_Checks')
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        df = pd.read_csv(locations_csv_src)
        self.get_z_slices_check_img(df,dst_dir)
        self.get_heatmap_of_xy(df, dst_dir)
    
        
    def save_locations_shape(self, locs_csv_src):
        
        dst = os.path.join(os.path.dirname(locs_csv_src), 'Locations_Shape.txt')
        f = open(dst, "a")
        df = pd.read_csv(locs_csv_src)
        
        hybs = df.hyb.unique()
        chs = df.ch.unique()
        i = 0
        for hyb in hybs:
            for ch in chs:
                df_ch = df.loc[(df['hyb'] == hyb) & (df['ch'] == ch)]
                f.write("Dots in Channel " + str(i) + ": " + str(df_ch.shape[0]) + "\n")
                i+=1
        
        f.close()
        
    def get_ave_over_hyb_ch_z(self, src, dst):
        
        df = pd.read_csv(src)
        df_aves = pd.DataFrame(columns = ['hyb', 'ch', 'z', 'ave_int', 'n_dots'])
    
        for hyb in df.hyb.unique():
            for ch in df.ch.unique():
                for z in df.z.unique():
                    df_hyb_ch_z = df[(df.hyb == hyb) & (df.z == z) & (df.ch == ch)]
                    dict_ave_row = {'hyb':hyb,'ch':ch,'z':z, 'ave_int':df_hyb_ch_z.int.mean(), \
                                    'n_dots':df_hyb_ch_z.shape[0]}
                    df_aves = df_aves.append(dict_ave_row, ignore_index = True)
                    
        df_aves.to_csv(dst, index=False)
    
 
    def run_dot_detection_2d(self):
        
        for z in range(self.num_zslices):
            
            #Run Dot Detection
            #--------------------------------------------------------------------
            df_locs = self.get_dot_locations(z_slice =z)
            #--------------------------------------------------------------------
            
            
            #Set path to save locations
            #--------------------------------------------------------------------
            if not os.path.exists(self.locations_dir ):
                os.makedirs(self.locations_dir )
            
            locations_file_name = 'locations_z_' + str(z) +'.csv'
        
            locations_path = os.path.join(self.locations_dir , locations_file_name)
            #--------------------------------------------------------------------
        
            
            #Save Locations
            #--------------------------------------------------------------------
            print("        Saving Locations to", locations_path, flush=True)
            
    
            df_locs.to_csv(locations_path, index = False)
            self.save_locations_shape(locations_path)
            #--------------------------------------------------------------------
            
        return locations_path

    def run_dot_detection(self):
        
        if self.dimensions == 2:
            self.run_dot_detection_2d()
            return None
            
        print("    Getting Dot Locations with", self.dot_detection, flush=True)
        
        #Run Dot Detection
        #--------------------------------------------------------------------
            
        df_locs = self.get_dot_locations()

        #--------------------------------------------------------------------
        
        
        #Set path to save locations
        #--------------------------------------------------------------------
        if not os.path.exists(self.locations_dir):
            os.makedirs(self.locations_dir)
        
    
        locations_path = os.path.join(self.locations_dir, 'locations.csv')
        #--------------------------------------------------------------------
    
        
        #Save Locations
        #--------------------------------------------------------------------
        print("        Saving Locations to", locations_path, flush=True)
        

        df_locs.to_csv(locations_path, index = False)
        self.save_locations_shape(locations_path)
        
        bright_analysis_dst = os.path.join(self.locations_dir, 'Average_Brightness_Analysis.csv')
        self.get_ave_over_hyb_ch_z(locations_path, bright_analysis_dst)
        self.get_location_checks(locations_path)
        #self.save_locs_shape(locations_path)
        #--------------------------------------------------------------------
        
        return locations_path
        
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
                offset = [np.round(float(off),3) for off in offset]
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
                temp_dir = os.path.join(main_dir, 'personal', 'temp', 'temp_dots')
                rand = rand_list[sub_dirs.index(sub_dir)]
                rand_dir = os.path.join(temp_dir, rand)
                if not os.path.exists(rand_dir):
                    os.mkdir(rand_dir)

                #------------------------------------------------
             
                print('Offset in DOt Detection Class', str(offset))
                
                print('========================================================================')
                
                print(f'{self.dot_detection=}')
                if 'top' in self.dot_detection:
                    
                    n_dots = int(self.dot_detection.split('top')[1].split('dots')[0])
                    
                    list_cmd = ['python', dot_detection_dir+ '/get_top_n_dots.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], '--analysis_name', self.analysis_name, \
                            '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--n_dots', n_dots, '--num_wav', self.num_wav, '--rand', rand_dir, \
                            '--num_z', self.num_z]
                    
                    list_cmd = [str(i) for i in list_cmd]
               
                    time_for_slurm = "0:10:00"
               
                elif self.dot_detection == "biggest jump":
                    

                    list_cmd = ['python', dot_detection_dir+ '/hist_jump.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--num_wav', self.num_wav,'--z_slices', z_slice]
                    
                    list_cmd = [str(i) for i in list_cmd]
                    
                    time_for_slurm = "0:10:00"            
                        
                elif self.dot_detection == "matlab 3d":
                    

                    list_cmd = ['python', dot_detection_dir + '/matlab_3d.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--num_wav', self.num_wav,'--z_slices', z_slice, '--nbins',  \
                            self.nbins, '--threshold', self.threshold]
                    
                    list_cmd = [str(i) for i in list_cmd]
                    
                    time_for_slurm = "0:10:00"
                    
                elif self.dot_detection == "adcg 2d":
                    

                    list_cmd = ['python', dot_detection_dir+ '/adcg_2d.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--num_wav', self.num_wav,
                            '--z_slices', z_slice, '--min_weight_adcg', self.min_weight_adcg, '--final_loss_adcg', self.final_loss_adcg]
                    
                    list_cmd = [str(i) for i in list_cmd]
                    
                    time_for_slurm = "4:00:00"
                
                elif self.dot_detection == "biggest jump 3d":
                    

                    list_cmd = ['python', dot_detection_dir+ '/hist_jump_3d.py', '--offset0', offset[0], '--offset1', offset[1], '--offset2', offset[2], \
                    '--analysis_name', self.analysis_name,  '--vis_dots', self.visualize_dots, '--back_subtract', self.background_subtraction, \
                            '--tiff_src', tiff_file_path,  '--norm', self.normalization, '--channels', self.decoding_individual, \
                            '--chromatic', self.chromatic_abberration, '--rand', rand_dir, '--gaussian', self.gaussian_fitting, \
                            '--radial_center', self.radial_center, '--strictness', self.strictness_dot_detection, '--num_wav',  \
                            self.num_wav, '--z_slices', z_slice, '--num_z', self.num_z, '--nbins', self.nbins, '--dot_radius', self.dot_radius, \
                            '--threshold', self.threshold, '--radius_step', self.radius_step, '--num_radii', self.num_radii]
                    
                    list_cmd = [str(i) for i in list_cmd]
                    
                    time_for_slurm = "0:35:00"            
                else:

                    
                    raise Exception("The dot detection argument was not valid.")    
                
                
                #Call Sbatch
                #------------------------------------------------
                cmd = ' '.join(list_cmd)
                print(f'{cmd=}')
                #print(f'{cmd=}')
                script_name = os.path.join(rand_dir, 'dot_detection.sh')
                with open(script_name , 'w') as f:
                    print('#!/bin/bash', file=f) 
                    print(cmd, file=f)  
                
                #os.system(cmd)
                out_path = os.path.join(rand_dir, 'slurm.out')
                call_me = ['sbatch', '--job-name', rand_list[sub_dirs.index(sub_dir)], '--output', out_path, "--time", time_for_slurm, "--mem-per-cpu", "10G", '--ntasks', '2', script_name]
                print(" ".join(call_me))
                subprocess.call(call_me)
                #------------------------------------------------
                
                
        while not are_jobs_finished(rand_list):
            print("Waiting for Dot Detection Jobs to Finish")
            time.sleep(30)
        

        df_locs = combine_locs(rand_list)
        
        #Delete the rand dirs
        #----------------------------------------------
        if self.debug_dot_detection == True:
            print('Did not delete dot detection directories')
            pass
        else:
            print('Did delete dot detection directories')
            for rand in rand_list:
                rand_dir = os.path.join(temp_dir, rand)
                shutil.rmtree(rand_dir)
        #----------------------------------------------
        
        return df_locs
        
if sys.argv[1] == 'debug_dot_class':
                       
    experiment_name = 'arun_1'
    personal='nrezaee'
    position = 'MMStack_Pos0.ome.tif'
    locations_dir=None
    analysis_name = 'test_form2_______strict_6.json'
    visualize_dots = True
    normalization = False
    background_subtraction = False
    decoding_individual = True
    chrom = False
    dot_detection = 'biggest jump 3d'
    gauss = False
    strict = 10
    dim = 3
    rad = False
    num_z = 7
    nbins = 100
    threshold = 300
    num_wav = 4
    z_slices = None
    dot_radius = 1
    radius_step = 2
    num_radii = 2
    debug_dot_detection = False
    min_weight_adcg = 1000
    final_loss_adcg = 1000
    
    dot_detection = Dot_Detection = (experiment_name, personal, position, locations_dir, \
                  analysis_name, visualize_dots, normalization, \
                  background_subtraction, decoding_individual, chrom, \
                  dot_detection, gauss, strict, dim, \
                  rad, num_z, nbins, threshold, num_wav,
                  z_slices, 
                   dot_radius,
                   radius_step, 
                   num_radii, 
                   debug_dot_detection,
                   min_weight_adcg, 
                   final_loss_adcg)
                   
    print(f'{dot_detection=}')
                   
    
                   
    
    
        
            
            
                