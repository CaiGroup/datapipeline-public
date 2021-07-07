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
import pandas as pd
import re
from helpers.excel2dict import get_dict_from_excel
import linecache


main_dir = '/groups/CaiLab'

def PrintException():

    #Print Exception with line number
    #-------------------------------------------------
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    #-------------------------------------------------

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))
    
def get_specific_positions(spec_positions, positions):
    
    """
    Inputs:
        spec_postions: list of numbers
        positions: list of MMStack_Pos{n}.ome.tif's
    Outpus:
        list of MMStack_Pos{n}.ome.tif's in spec_positions
    """
    
    spec_positions = spec_positions.replace(' ', '').split(',')
    print(f'{spec_positions=}')
    #Split positions to get position numbers
    positions_split = [re.split('Pos|,|.ome.tif', position) 
                       for position in positions]
    
    #Check if position number in .ome.tif's and add to list
    spec_positions_split = []
    for spec_position in spec_positions:
        for position_split in positions_split:
            if spec_position in position_split:
                print(f'{position_split=}')
                spec_positions_split.append(position_split)
    
    #Combine splitted positions
    result_positions = [spec_position_split[0] + 'Pos' + spec_position_split[1] \
                    + '.ome.tif' for spec_position_split in spec_positions_split]
    
    return result_positions
    
    
def check_if_all_hybs_are_present(path_to_experiment_dir):
    """
    Runs a check to see if all hybs are in an experiment
    Input Example
        /groups/CaiLab/personal/nrezaee/2020-08-08-takei
    """
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
    
def read_json(json_name, source_of_jsons):
    """
    Read json file and make the keys lowercase 
    except for personl and experiment name
    """
    
    #Set json_path and get open it
    #-----------------------------------------------------
    json_file_path = os.path.join(source_of_jsons, json_name)
    with open(json_file_path) as json_file: 
        non_lowercase_data = json.load(json_file) 
    #-----------------------------------------------------
    
    #Make everything lowercase
    #-----------------------------------------------------
    data = {}
    for key, value in non_lowercase_data.items():
        if type(value) == str:
            if key.lower() == 'personal' or key.lower() == 'experiment_name':
                data[key.lower()] = value
            else:
                data[key.lower()] = value.lower()
        else:
            data[key.lower()] = value
    #-----------------------------------------------------
    
    return data, json_file_path
    
def read_xlsx(json_name, source_of_jsons):
    
    json_file_path = os.path.join(args.source_of_jsons, json_name)
    data = get_dict_from_excel(json_file_path)
    
    data['clusters'] = {}
    data['clusters']['ntasks'] = "1"
    data['clusters']['mem-per-cpu'] = "10G"
    

    os.remove(json_file_path)
    pre, ext = os.path.splitext(json_file_path)

    json_file_path = pre 
    json_name = os.path.basename(json_file_path) + '.json'

    with open(json_file_path, 'w') as fp:
        json.dump(data, fp)
    
    return data, json_file_path
        
def make_analysis_dirs(data):
    """
    Make directories from input 
    """
    
    #Make personal directory
    #-----------------------------------------------------
    personal_dir = os.path.join(main_dir, 'analyses', data['personal'])
    if not os.path.isdir(personal_dir):
        os.mkdir(personal_dir)
    #-----------------------------------------------------
    
    #Make experiment directory
    #-----------------------------------------------------
    exp_analyses_dir = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'])
    if not os.path.isdir(exp_analyses_dir):
        os.mkdir(exp_analyses_dir)
    #-----------------------------------------------------
    
    #Get analyses
    #-----------------------------------------------------
    analyses_in_exp = os.listdir(exp_analyses_dir)
    analysis_name = json_name.split('.json')[0]
    #-----------------------------------------------------
    
    return analyses_in_exp, analysis_name, exp_analyses_dir
    
def check_if_analysis_exists(analyses_in_exp, analysis_name, source_of_jsons, exp_analyses_dir, data):
    """
    This function will throw an error if an analysis exists under the same name
    
    """

    #Check if analysis name has already been used
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
            
def move_json_file_to_analysis_dir(json_name, main_dir, data):
    """
    Move json to analysis directory
    The json is copied over to save the parameters
    """

    #Move the json file analyses directory
    #----------------------------------------------------------
    analysis_name = json_name.split('.json')[0]
     
    new_json_path = os.path.join(main_dir, 'analyses', data['personal'], data['experiment_name'], analysis_name, json_name)
        
    shutil.move(json_file_path, new_json_path)
    #----------------------------------------------------------
    
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
    
def get_positions_in_data(data, main_dir):
    """
    Check to see if specific positions are specified in the json
    Then get those positions and return
    """

    #Get single position
    #----------------------------------------------------------
    if 'decoding with previous locations variable' in data.keys():
        if data['decoding with previous locations variable'] == 'true':
            
            positions = ['MMStack_Pos0.ome.tif']

    else:
        
        exp_dir = os.path.join(main_dir, "personal", data["personal"], "raw", data["experiment_name"])
        
        hybs = [hyb for hyb in os.listdir(exp_dir) if 'Hyb' in hyb]
        
        path_to_sub_dir = os.path.join(exp_dir, hybs[0])
        
        positions = os.listdir(path_to_sub_dir)
        
        
        if 'positions' in data.keys():
            if data['positions'] != 'NaN':
                print(f'{data["positions"]=}')
                if data['positions'].replace(' ', '') != '':
                    if hasNumbers(data['positions']):
                        positions = get_specific_positions(data['positions'], positions)
                        
        print(2)

    return positions
    

def get_slurm_params(json_name, data, position):
    """
    Set slurm parameters for job which are specified in the json file
    """

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
        time = '10:00:00'
        
    print("    time:", time, flush=True)
    #--------------------------------------------------------------
    
    #Define output file
    #--------------------------------------------------------------
    output_dir = os.path.join(main_dir, 'analyses/', data['personal'], data['experiment_name'], \
                                    json_name.split('.json')[0], position.split('.ome')[0], 'Output')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file_path = os.path.join(output_dir, 'slurm_output.out')
    #--------------------------------------------------------------
    
    return batch_name, nodes, ntasks, mem_per_cpu, time, output_file_path, running_in_slurm 

def check_if_all_hybs_exist(data):
    """
    Check to see if all hybs exist in data directory
    """
    
    #Glob all hybs
    #--------------------------------------------------------------
    data_dir = os.path.join('/groups/CaiLab/personal/', data['personal'], 'raw', data['experiment_name'])
    glob_me = os.path.join(data_dir, '*')
    #--------------------------------------------------------------
    
    #Check to see if a hyb isnt present
    #--------------------------------------------------------------
    bool_present, diff_hybs = check_if_all_hybs_are_present(glob_me)
    if bool_present == False:
        str_hybs = ','.join(str(e) for e in diff_hybs)
        warning_message = "Warning the following Hybs seem to be missing from the dataset: " + str_hybs 
        print(warning_message)
    #--------------------------------------------------------------
    
    
def create_multiple_jsons_for_thresholds(json_src):
    """
    Create multiple jsons for thresholds if "multiple" or "multiple low"
    """
    
    #Open Json
    #--------------------------------------------------------------
    with open(json_src) as json_file:
        data = json.load(json_file)
    #--------------------------------------------------------------
        
    #Check for multiple strictnesses
    #--------------------------------------------------------------
    if 'strictness' in data.keys():
        if data['strictness'] == 'multiple':
            for i in range(0,10,2):
                
                #Make json with strictness
                #--------------------------------------------------------------
                new_json_src = json_src.split('.json')[0] + '_______strict_'+str(i)+'.json'
                data['strictness'] = i
                with open(new_json_src, 'w') as outfile:
                    json.dump(data, outfile)
                #--------------------------------------------------------------
            os.remove(json_src)
                
        elif data['strictness'] == 'multiple low':
            for i in range(-5,5,2):
                
                #Make json with strictness
                #--------------------------------------------------------------
                new_json_src = json_src.split('.json')[0] + '_______strict_'+str(i)+'.json'
                data['strictness'] = i
                with open(new_json_src, 'w') as outfile:
                    json.dump(data, outfile)
                #--------------------------------------------------------------
                
            os.remove(json_src)
    #--------------------------------------------------------------
    
    
def check_for_multiple_thresholds(json_srcs, main_dir):
    """
    Check if multiple strictnesses in json file
    
    """

    for json_src in json_srcs:
        json_full_src = os.path.join(main_dir, json_src)
        create_multiple_jsons_for_thresholds(json_full_src)

#Set Arguments
#----------------------------------------------------------
main_dir = '/groups/CaiLab'
parser = argparse.ArgumentParser()
parser.add_argument("--source_of_jsons", help="Directory for source of jsons", nargs='?')
args = parser.parse_args()

if args.source_of_jsons == None:
    args.source_of_jsons = os.path.join(main_dir, 'json_analyses')
    
check_for_multiple_thresholds(os.listdir(args.source_of_jsons) , args.source_of_jsons)
#----------------------------------------------------------


# Getting the list of jsons in the directory
#--------------------------------------------------------------
dir = os.listdir(args.source_of_jsons) 
#--------------------------------------------------------------
print(f'{dir=}')


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
    
            filename, file_extension = os.path.splitext(json_name)
            if file_extension == '.json':
                
                data, json_file_path = read_json(json_name, args.source_of_jsons)

            elif file_extension == '.xlsx':
                data, json_file_path = read_xlsx(json_name, args.source_of_jsons)

            #Check if all Hybs are present
            #--------------------------------------------------------------------------
            if 'decoding with previous locations variable' in data.keys():
                if data['decoding with previous locations variable'] == 'true':
                    pass
        
            else:
                pass
                #check_if_all_hybs_exist(data)
                
            analyses_in_exp, analysis_name , exp_analyses_dir = make_analysis_dirs(data)
            
            #Try Statement to see if the same analysis name has been used
            #====================================================================
            try:

                check_if_analysis_exists(analyses_in_exp, analysis_name, args.source_of_jsons, exp_analyses_dir, data)

                
                #Make specific analyeses Directory for Experiment
                #----------------------------------------
                analysis_name = json_name.split('.json')[0]
                analyses_dir = os.path.join(exp_analyses_dir, analysis_name)
                if not os.path.isdir(analyses_dir):
                    os.mkdir(analyses_dir)
                #----------------------------------------
                
                move_json_file_to_analysis_dir(json_name, main_dir, data)

                positions = get_positions_in_data(data, main_dir)
                
                print(f'{positions=}')
                # Go through each position
                #----------------------------------------------------------
                for position in positions:
                    #Make Position Directory
                    #----------------------------------------------------------
                    position_dir = os.path.join(exp_analyses_dir, analysis_name, position.split('.ome')[0])
                    if not os.path.isdir(position_dir):
                        os.mkdir(position_dir)
                    #----------------------------------------------------------
                    
                    if 'email' in data.keys():
                        email = data['email']
                    else:
                        email = 'none'
        
                    print("Running", json_name, "for", position, flush=True)
                    print(2)
                    #Checking for SLURM commands
                    #---------------------------------------------------------------------------------
                    if "clusters" in data.keys():
                        
                        batch_name, nodes, ntasks, mem_per_cpu, time, output_file_path, running_in_slurm = get_slurm_params(json_name, data, position)
                        
                        #Run slurm Command
                        #--------------------------------------------------------------
                        kickoff_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kickoff_analysis.sh")
                        subprocess.call(["sbatch", "--job-name", batch_name, \
                                         "--nodes", nodes, \
                                         "--ntasks", ntasks, \
                                         "--mem-per-cpu", mem_per_cpu, \
                                         "--time", time, \
                                         "--mail-type=BEGIN", "--mail-type=END", "--mail-type=FAIL", \
                                         "--output", output_file_path, \
                                         kickoff_script, json_name, position, data["personal"], data["experiment_name"], \
                                         running_in_slurm, os.path.dirname(os.path.abspath(__file__)), email])
                        #--------------------------------------------------------------
        
                    else:
                        
                        
                        
                        #Running in Slurm Variable to False
                        #--------------------------------------------------------------
                        running_in_slurm = 'False'
                        #--------------------------------------------------------------     
                        
        
                        #Run Without Slurm
                        #--------------------------------------------------------------
                        kickoff_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kickoff_analysis.sh")
                        subprocess.call(["bash", kickoff_script, json_name, position, data["personal"], data["experiment_name"], running_in_slurm, os.path.dirname(os.path.abspath(__file__)), email ])
                        #--------------------------------------------------------------
        
            
            except Exception as e:
                PrintException()
            #====================================================================
            #End of Try Statement to see if the same analysis name has been used
            
            
             
        except Exception as e: 
            
            #Remove json file in 
            json_file_path = os.path.join(args.source_of_jsons, json_name)
            os.remove(json_file_path)
            
            
            print(e)    
        #============================================================================================================================    
        #End of Try statement in case of error in opening json or making directories    
            
            
            