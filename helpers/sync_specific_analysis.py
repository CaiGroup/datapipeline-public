import os
import sys
import glob

def are_logs_finished(analysis_dir):
    glob_me = os.path.join(analysis_dir, 'MMStack_Pos*', 'Logging.txt')
    
    log_file_paths = glob.glob(glob_me)
    
    bool_pos_done = []
    
    for log_file in log_file_paths:
        file = open(log_file,mode='r')
        content = file.read()
        file.close()
        bool_pos_done.append('Finished with Analysis of Position' in content)
        
    return all(bool_pos_done)
    
def send_analysis_to_onedrive(analysis_dir):
    
    if are_logs_finished(analysis_dir):
        spec_analysis = analysis_dir.split('analyses')[1]
        
        print(f'{spec_analysis=}')
        cmd = 'rclone copy /groups/CaiLab/analyses' + spec_analysis +  ' onedrive_caltech:Analyses' + spec_analysis
        
        print(f'{cmd=}')
    
        os.system(cmd)
        

if sys.argv[1] == 'debug_rclone':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/form_takei'
    send_analysis_to_onedrive(analysis_dir)