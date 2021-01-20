import json
import os
import shutil
import filecmp
import sys
from pathlib import Path
import check_tests
import json
import glob

main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']


def delete_files_in_json_analyses(run_jsons_dir):
    
    files = glob.glob(os.path.join(run_jsons_dir, '*'))
    if len(files) != 0:
        for f in files:
            os.remove(f)

def delete_previous_analyses():
    test_json_file_paths = glob.glob(os.path.join(run_jsons_dir,'*'))
    
    for json_path in test_json_file_paths:
        
        json_name = os.path.basename(json_path).split('.')[0]
        
        with open(json_path) as f:
            json_dict = json.load(f)
        
        analysis_dir_to_delete = os.path.join(main_dir, 'analyses', json_dict['personal'], json_dict['experiment_name'], json_name)
        
        print(f'{analysis_dir_to_delete=}')
            
        if os.path.isdir(analysis_dir_to_delete):    
            shutil.rmtree(analysis_dir_to_delete)

def get_experiment_name(json_file_name):
    json_path = os.path.join(os.getcwd(), 'deployment_tests', 'test_jsons', json_file_name)
    
    with open(json_path) as f:
        json_dict = json.load(f)
        
    return json_dict['experiment_name']



run_jsons_dir = os.path.join(str(Path.home()), 'json_analyses')
delete_files_in_json_analyses(run_jsons_dir) 

#Copy All the test Jsons
#--------------------------------------------------------------------------------------
cwd = os.getcwd()
test_jsons_dir = os.path.join(cwd, 'deployment_tests', 'test_jsons')
if len(sys.argv) == 1:
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_across.json'), os.path.join(run_jsons_dir, '3d_across.json'))
elif len(sys.argv) == 'dry':
    pass
elif sys.argv[1] == '2d':
    shutil.copyfile(os.path.join(test_jsons_dir, '2d_across.json'), run_jsons_dir+'/2d_across.json')
    shutil.copyfile(os.path.join(test_jsons_dir, '2d_indiv.json'), run_jsons_dir+'/2d_indiv.json')
elif sys.argv[1] == '3d':
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_across.json'), run_jsons_dir+'/3d_across.json')
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_indiv.json'), run_jsons_dir+'/3d_indiv.json')
elif sys.argv[1] == 'across':
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_across.json'), run_jsons_dir+'/3d_across.json')
    shutil.copyfile(os.path.join(test_jsons_dir, '2d_across.json'), run_jsons_dir+'/2d_across.json')
elif sys.argv[1] == 'indiv':
    shutil.copyfile(os.path.join(test_jsons_dir, '2d_indiv.json'), run_jsons_dir+'/2d_indiv.json')
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_indiv.json'), run_jsons_dir+'/3d_indiv.json')
    
elif sys.argv[1] == 'seg':
    shutil.copyfile(os.path.join(test_jsons_dir, '3d_across_seg.json'), run_jsons_dir+'/3d_across_seg.json')
elif sys.argv[1] == 'all':
    shutil.copytree(test_jsons_dir, run_jsons_dir, dirs_exist_ok=True)
#--------------------------------------------------------------------------------------


#Delete the Previous Analyses
#--------------------------------------------------------------------------------------
delete_previous_analyses()
#--------------------------------------------------------------------------------------   


#Runs the Tests
#--------------------------------------------------------------------------------------
os.system('sh run_cron.sh ' + run_jsons_dir)
#--------------------------------------------------------------------------------------


if len(sys.argv) == 1 :
    check_tests.check_3d_across_test()
    
elif sys.argv == '3d': 

    check_tests.check_3d_across_test()
    check_tests.check_3d_indiv_test()    
    
elif sys.argv[1] == 'dry':

    check_tests.check_3d_across_test()
    check_tests.check_3d_indiv_test()

        
        
        
