import json
import os
import shutil


main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']

#Function to insert dictionary as json file for testing
#----------------------------------------------------------------------------
def insert_test(json_as_dict, name_of_analysis):

    #Put file in source of jsons
    #------------------------------------
    json_in_json_source = os.path.join('/home/nrezaee/json_analyses/', name_of_analysis + '.json')
    
    with open(json_in_json_source, 'w') as fp:
        json.dump(json_as_dict, fp)
    #------------------------------------
    
    #Delete Analysis folder if it exists
    #------------------------------------
    former_analysis_dir = os.path.join(main_dir, 'analyses/nrezaee/', json_as_dict['experiment_name'],  name_of_analysis)
    
    if os.path.isdir(former_analysis_dir):
        shutil.rmtree(former_analysis_dir)
    #------------------------------------