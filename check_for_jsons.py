"""
The point of this script to look for json files in the json directory. The json 
directory by default is /groups/CaiLab/json_analyses, but 
can be set to a different source for debugging with the 
--source_of_jsons argument. 

This script grabs information for the json file and kicks off the kickoff_analysis.sh
script which can run on a slurm job if specified in the json file.
"""

import os 
import subprocess
import json
import pathlib 
import shutil
import argparse
import sys
import warnings
import glob
import numpy as np


if os.environ.get('DATA_PIPELINE_MAIN_DIR') is not None:
    main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']
else:
    raise Exception("The Main Directory env variable is not set. Set DATA_PIPELINE_MAIN_DIR!!!!!!!!")

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

def check_if_all_hybs_are_present(path_to_experiment_dir):
    #Get all files in path
    #-------------------------------------------------
    hyb_dirs = glob.glob(path_to_experiment_dir)
    #-------------------------------------------------
    
    #Remove anything that is not a Hyb
    #-------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in hyb_dirs if 'HybCycle' in hyb_dir]
    #-------------------------------------------------
    
    #Split hybs to get numbers
    #-------------------------------------------------
    split_word = 'Cycle_'
    for index in range(len(hyb_dirs)):

        hyb_dirs[index] = hyb_dirs[index].split(split_word)
 
        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    #-------------------------------------------------
    
    #Sort the Hybs
    #-------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    #-------------------------------------------------
    
    #Get Hyb nums and "Should be" Hyb nums
    #-------------------------------------------------
    splitted = np.array(sorted_hyb_dirs)
    str_hyb_nums = splitted[:,1]
    hyb_nums = [int(hyb_num) for hyb_num in str_hyb_nums]
    should_be_hybs = list(range(max(hyb_nums)+1))
    #-------------------------------------------------
    
    #Get Bool and Difference in Hybs
    #-------------------------------------------------
    bool_present = (hyb_nums == should_be_hybs)
    diff_hybs = Diff(hyb_nums, should_be_hybs)
    #-------------------------------------------------
    
    return bool_present, diff_hybs

#Set Arguments
#----------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--source_of_jsons", help="Directory for source of jsons", nargs='?')
args = parser.parse_args()

if args.source_of_jsons == None:
    args.source_of_jsons = os.path.join(main_dir, 'json_analyses')
#----------------------------------------------------------


# Getting the list of jsons in the directory
#--------------------------------------------------------------
dir = os.listdir(args.source_of_jsons) 
#--------------------------------------------------------------
  
  
# Checking if the list is empty or not 
#--------------------------------------------------------------
if len(dir) == 0: 
    print("No Json Analyses in Directory branch")
    pass
    
else: 
    
    for json_name in dir:
  
        #Try statement in case of error in opening json or making directories
        #============================================================================================================================
        try:
            #Path to Json file in Json Analyses
            #----------------------------------------------------------
            json_file_path = os.path.join(args.source_of_jsons, json_name)
            
            
            with open(json_file_path) as json_file: 
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
            #----------------------------------------------------------

            #Check if all Hybs are present
            #--------------------------------------------------------------------------
            if 'decoding with previous locations variable' in data.keys():
                if data['decoding with previous locations variable'] != 'true':
                    data_dir = os.path.join('/groups/CaiLab/personal/', data['personal'], 'raw', data['experiment_name'])
                    glob_me = os.path.join(data_dir, '*')
                    bool_present, diff_hybs = check_if_all_hybs_are_present(glob_me)
                    
                    if bool_present == False:
            
                        str_hybs = ','.join(str(e) for e in diff_hybs)
                        warning_message = "Warning the following Hybs seem to be missing from the dataset: " + str_hybs 
                        print(warning_message)
            #--------------------------------------------------------------------------
        
            #Make Directories
            #--------------------------------------------------------------------------
        
            #Personal in analyses directory
            #----------------------------------------
            personal_dir = os.path.join(main_dir, 'analyses', data['personal'])
            if not os.path.isdir(personal_dir):
                os.mkdir(personal_dir)
            #----------------------------------------
            
        
            #Make personal directory in Analyses directory
            #----------------------------------------
            exp_analyses_dir = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'])
            if not os.path.isdir(exp_analyses_dir):
                os.mkdir(exp_analyses_dir)
            #----------------------------------------
                
            
            #Check to see if analysis already exists in experiment
            #-----------------------------------------
            analyses_in_exp = os.listdir(exp_analyses_dir)
            analysis_name = json_name.split('.json')[0]
            
            
            #Try Statement to see if the same analysis name has been used
            #====================================================================
            try:
                
                #Checking to see if analysis already exists
                #-----------------------------------------
                for analysis in analyses_in_exp:
                    
                    if analysis == analysis_name:
                        
                        #Remove json in json source directory
                        #-----------------------------------------
                        json_file_path = os.path.join(args.source_of_jsons, analysis+'.json')
                        os.remove(json_file_path)
                        #-----------------------------------------
                        
                        #Throw exception
                        #-----------------------------------------
                        exception_message = "Error Error An analysis of " +analysis + " already exists for " + data['experiment_name'] + \
                                        " at " + os.path.join(exp_analyses_dir, analysis_name)
                        raise Exception(exception_message)
                        #-----------------------------------------
                 #----------------------------------------
                
                
                
                #Make specific analyeses Directory for Experiment
                #----------------------------------------
                analysis_name = json_name.split('.json')[0]
                analyses_dir = os.path.join(exp_analyses_dir, analysis_name)
                if not os.path.isdir(analyses_dir):
                    os.mkdir(analyses_dir)
                #----------------------------------------
                
                #Move the json file analyses directory
                #----------------------------------------------------------
                analysis_name = os.path.splitext(json_name)[0]
                 
                new_json_path = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'], analysis_name, json_name)
                    
                shutil.move(json_file_path, new_json_path)
                #----------------------------------------------------------
                
                
                #Get Different Positions
                #----------------------------------------------------------
           
                if 'decoding with previous locations variable' in data.keys():
                    if data['decoding with previous locations variable'] == 'true':
                        
                        positions = ['MMStack_Pos0.ome.tif']
                        
                        
                else:
                    
                    exp_dir = os.path.join(main_dir, "personal", data["personal"], "raw", data["experiment_name"])
                    
                    hybs = [hyb for hyb in os.listdir(exp_dir) if 'Hyb' in hyb]
                    
                    path_to_sub_dir = os.path.join(exp_dir, hybs[0])
                    
                    positions = os.listdir(path_to_sub_dir)
                #----------------------------------------------------------
                
                
                # Go through each position
                #----------------------------------------------------------
                for position in positions:
                    
                    
                    #Make Position Directory
                    #----------------------------------------------------------
                    position_dir = os.path.join(exp_analyses_dir, analysis_name, position.split('.ome')[0])
                    if not os.path.isdir(position_dir):
                        os.mkdir(position_dir)
                    #----------------------------------------------------------
                    
                    print("Running", json_name, "for", position, flush=True)
                    
                    #Checking for SLURM commands
                    #---------------------------------------------------------------------------------
                    if "clusters" in data.keys():
                        
                        #Running in Slurm Variable to True
                        #--------------------------------------------------------------
                        running_in_slurm = 'True'
                        #--------------------------------------------------------------
                        
                        
                        print("Slurm Parameters:")
                        
                        #Get Name of job 
                        #--------------------------------------------------------------
                        analysis_name, dot_json = os.path.splitext(json_name)
                        
                        batch_name = analysis_name
                        #--------------------------------------------------------------
                        
                        #Get ntasks
                        #--------------------------------------------------------------
                        if "ntasks" in data["clusters"].keys():
                            ntasks = data['clusters']["ntasks"]
                            
                        else:
                            ntasks = '1'
                            
                        print("    ntasks:", ntasks, flush=True)
                        #--------------------------------------------------------------
                        
                        #Get Nodes
                        #--------------------------------------------------------------
                        if "nodes" in data["clusters"].keys():
                            nodes = data['clusters']["nodes"]
                            
                        else:
                            nodes = '1'
                        
                        print("    nodes:", nodes, flush=True)
                        #--------------------------------------------------------------
                        
                        #Get MEM Per CPU
                        #--------------------------------------------------------------
                        if "mem-per-cpu" in data["clusters"].keys():
                            mem_per_cpu = data['clusters']["mem-per-cpu"]
                            
                        else:
                            mem_per_cpu = '1G'
                            
                        print("    mem_per_cpu:", mem_per_cpu, flush=True)
                        #--------------------------------------------------------------
                        
                        #Send Email to User
                        #--------------------------------------------------------------
                        if "email" in data["clusters"].keys():
                            email = data['clusters']["email"]
                            
                            print("    Email for Slurm Notifications:", email, flush=True)
                            
                        else:
                            email = 'nrezaeegradschools@gmail.com'
                        
                            print("    No email set for Slurm Notifications", flush=True)
                        #--------------------------------------------------------------
                        
                        #Send Email to User
                        #--------------------------------------------------------------
                        if "time" in data["clusters"].keys():
                            time = data['clusters']["time"]
                            
                        else:
                            time = '05:00:00'
                            
                        print("    time:", time, flush=True)
        
                        #--------------------------------------------------------------
                        
                        #Define output file
                        #--------------------------------------------------------------
                        output_dir = os.path.join(main_dir, 'analyses/', data['personal'], data['experiment_name'], \
                                                        json_name.split('.json')[0], 'Output')
                        
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        output_file_path = os.path.join(output_dir, 'slurm_output.out')
                        #--------------------------------------------------------------
                        
        
                        #Run slurm Command
                        #--------------------------------------------------------------
                        kickoff_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kickoff_analysis.sh")
                        subprocess.call(["sbatch", "--job-name", batch_name, \
                                         "--nodes", nodes, \
                                         "--ntasks", ntasks, \
                                         "--mem-per-cpu", mem_per_cpu, \
                                         "--time", time, \
                                         "--mail-user",  email, \
                                         "--mail-type=BEGIN", "--mail-type=END", "--mail-type=FAIL", \
                                         "--output", output_file_path, \
                                         kickoff_script, json_name, position, data["personal"], data["experiment_name"], \
                                         running_in_slurm, os.path.dirname(os.path.abspath(__file__))])
                        #--------------------------------------------------------------
        
                    else:
                        
                        
                        
                        #Running in Slurm Variable to False
                        #--------------------------------------------------------------
                        running_in_slurm = 'False'
                        #--------------------------------------------------------------     
                        
        
                        #Run Without Slurm
                        #--------------------------------------------------------------
                        kickoff_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kickoff_analysis.sh")
                        subprocess.call(["bash", kickoff_script, json_name, position, data["personal"], data["experiment_name"], running_in_slurm, os.path.dirname(os.path.abspath(__file__)) ])
                        #--------------------------------------------------------------
        
            
            except Exception as e:
                print(e)
            #====================================================================
            #End of Try Statement to see if the same analysis name has been used
            
            
             
        except Exception as e: 
            
            #Remove json file in 
            json_file_path = os.path.join(args.source_of_jsons, json_name)
            os.remove(json_file_path)
            
            
            print(e)    
        #============================================================================================================================    
        #End of Try statement in case of error in opening json or making directories    
            
            
            