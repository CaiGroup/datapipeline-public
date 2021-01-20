import os 
import glob
import numpy as np
import scipy.io
import json

def get_pos_array(src_dir):
    
    
    #Get all files in path
    #-------------------------------------------------
    tiffs = glob.glob(os.path.join(src_dir,'*'))
    #print(tiffs)
    #-------------------------------------------------

    pos_array = [int(tiff.split('.ome')[0].split('Pos')[1]) for tiff in tiffs]
    
    pos_array.sort()
    
    return pos_array

def run_beads(beads_dir, t_forms_dest):
    
    pos_array = get_pos_array(beads_dir)

    num_channels = 4
    
    assert len(pos_array) != 0, "There must be a beads directory located at /persona/<user>/raw/<exp_name>/beads/"
    
    #Creating Matlab Command
    #------------------------------------------------------------------
    cmd = """  matlab -r "addpath('/home/nrezaee/test_cronjob/chromatic_abberation/scripts'); beadtformglobal( '{0}' , {1}, {2}, '{3}'); quit"; """ 

    cmd = cmd.format(beads_dir, num_channels, pos_array, t_forms_dest)
    #------------------------------------------------------------------
    
    
    #Running Matlab Command
    #------------------------------------------------------------------
    print("Running Matlab Command for Chromatic Abberation:", cmd, flush=True)

    os.system(cmd)
    #------------------------------------------------------------------
    
    
    #Get offset from mat file 
    #------------------------------------------------------------------
    path_to_mat = os.path.join(t_forms_dest, 't_form_variables.mat')
    
    globaltform = scipy.io.loadmat(path_to_mat)['globaltform']
    
    offsets = {}
    
    #Retrieving Offset from mat 
    #---------------------------------------
    for index in range(globaltform.shape[0]):
        
        key = 'Channel '+ str(index)
        
        globaltform[index][0][3][:3][abs(globaltform[index][0][3][:3]) < .0001] =0
        
        offsets[key] = globaltform[index][0][3][:3].tolist()
    #---------------------------------------
    
    
    print(f'{offsets=}')
    
    offsets_dest = os.path.join(t_forms_dest, 'chromatic_offsets.json')
    
    with open(offsets_dest, 'w') as fp:
        json.dump(offsets, fp)
    
    
    
    return None
    
    
#Tests
#------------------------------------------------------------------
# beads_dir= '/groups/CaiLab/personal/nrezaee/raw/test1-beads/beads/'

# t_forms_dest = '/home/nrezaee/test_cronjob/chromatic_abberation/'

# run_beads(beads_dir, t_forms_dest)
    