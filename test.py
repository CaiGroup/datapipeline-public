import os 
import json 
import argparse
import sys
import shutil



#Set Arguments
#----------------------------------------------------------
# parser = argparse.ArgumentParser()
# parser.add_argument("--json_name", help="name of json", required=True)
# args = parser.parse_args()
#----------------------------------------------------------
json_name = sys.argv[1]

  
# Opening JSON file 
#----------------------------------------------------------
json_path = os.path.join('/home/nrezaee/test_analyses/', json_name)

with open(json_path) as json_file: 
    analysis_dict = json.load(json_file)
#----------------------------------------------------------

#Remove past analysis
#----------------------------------------------------------
path_of_past_analysis = os.path.join('/groups/CaiLab/analyses/', analysis_dict['personal'], \
                                     analysis_dict['experiment_name'], json_name.split('.json')[0])

if os.path.exists(path_of_past_analysis):
        
    print(f'{path_of_past_analysis=}')
    shutil.rmtree(path_of_past_analysis)
#----------------------------------------------------------


#Copy file to source of jsons
#----------------------------------------------------------
shutil.copyfile(json_path, os.path.join('/home/nrezaee/json_analyses', json_name))
#----------------------------------------------------------


#Run test
#----------------------------------------------------------
os.system('sh run_cron.sh /home/nrezaee/json_analyses')
#----------------------------------------------------------
