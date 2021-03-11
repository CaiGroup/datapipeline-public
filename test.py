import os 
import json 
import argparse
import sys
import shutil
import pandas as pd
from helpers.excel2dict import get_dict_from_excel

def remove_clusters(json_src):
    with open(json_src) as f:
        data = json.load(f)

    del data['clusters']
    
    with open(json_src, "w") as outfile:  
        json.dump(data, outfile)
        
    return data

json_name = sys.argv[1]
 
# Opening JSON file 
#----------------------------------------------------------
json_path = os.path.join('/home/nrezaee/test_analyses/', json_name)

filename, file_extension = os.path.splitext(json_name)
if file_extension == '.json':
    with open(json_path) as json_file: 
        analysis_dict = json.load(json_file)
        
elif file_extension == '.xlsx':
    analysis_dict = get_dict_from_excel(json_path)
    
#----------------------------------------------------------

print(f'{analysis_dict=}')
#Remove past analysis
#----------------------------------------------------------
path_of_past_analysis = os.path.join('/groups/CaiLab/analyses/', analysis_dict['personal'], \
                                     analysis_dict['experiment_name'], json_name.split('.json')[0].split('.xlsx')[0])

print(f'{path_of_past_analysis=}')
print(1)
if os.path.exists(path_of_past_analysis):
    print('hi')
    print(f'{path_of_past_analysis=}')
    shutil.rmtree(path_of_past_analysis)
#----------------------------------------------------------


#Copy file to source of jsons
#----------------------------------------------------------
if len(sys.argv) > 2:
    if sys.argv[2] == 'no_slurm':
        remove_clusters(json_path)
        
shutil.copyfile(json_path, os.path.join('/home/nrezaee/json_analyses', json_name))
#----------------------------------------------------------


#Run test
#----------------------------------------------------------
os.system('sh run_cron.sh /home/nrezaee/json_analyses')
#----------------------------------------------------------
