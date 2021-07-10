import os
import numpy as np
from scipy.io import loadmat

def decoding(barcode_src , locations_src, dest, min_seeds):
    
    
    #Get rounds and channels of experiment
    #-------------------------------------------------------------------
    barcodes = loadmat(barcode_src)["barcodekey"]

    num_of_rounds = barcodes[0][0][0].shape[1]
    
    channels_per_round = np.max(barcodes[0][0][0][:200])
    
    total_number_of_channels = num_of_rounds*channels_per_round
    #-------------------------------------------------------------------
    
    
    #Check if total channels is divisible by rounds
    #-------------------------------------------------------------------
    assert total_number_of_channels % num_of_rounds == 0
    #-------------------------------------------------------------------
    
    
    
    #Create Matlab Command
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');main_previous_points_decoding({1}', '{2}', '{3}', {4}, {5}, {6}, '{7}'); quit"; """ 
    
    cwd = os.getcwd()
    
    print(f'{cwd=}')
   
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    
    decoding_dir = os.path.join(cwd, 'decoding', 'helpers')

    
    cmd = cmd.format(decoding_dir, barcode_src, locations_src, dest, num_of_rounds, total_number_of_channels, allowed_diff, min_seeds)
    
    print(f'{cmd=}')

    #-------------------------------------------------------------------
    
    #Run Matlab Command
    #-------------------------------------------------------------------
    os.system(cmd)
    #-------------------------------------------------------------------
    
    return None





