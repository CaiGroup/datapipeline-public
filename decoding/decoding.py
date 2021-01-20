import os
import numpy as np
from scipy.io import loadmat

def decoding(barcode_src ,locations_src, dest, allowed_diff, min_seeds, channel_index = None, number_of_individual_channels_for_decoding=None):
    
    
    #Get rounds and channels of experiment
    #-------------------------------------------------------------------
    print(f'{barcode_src=}')
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
    cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """ 
    
    cwd = os.getcwd()
    
    print(f'{cwd=}')
    
    
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    
    decoding_dir = os.path.join(cwd, 'decoding', 'helpers')
    
    if channel_index == None and number_of_individual_channels_for_decoding == None:
        
        print(f'{min_seeds=}')
        
        cmd = cmd.format(decoding_dir, barcode_src, locations_src, dest, num_of_rounds, total_number_of_channels, '[]', '[]', allowed_diff, min_seeds)
        
        
        print(f'{cmd=}')
    else:
        
        print(f'{type(channel_index)=}')
        print(f'{type(number_of_individual_channels_for_decoding)=}')
        
        print(f'{channel_index=}')
        print(f'{number_of_individual_channels_for_decoding=}')
        
    
        cmd = cmd.format(decoding_dir, barcode_src, locations_src, dest, num_of_rounds, total_number_of_channels, \
        channel_index+1, number_of_individual_channels_for_decoding, allowed_diff, min_seeds)
        
    #print("Matlab Command for Decoding:", cmd, flush=True)
    #-------------------------------------------------------------------
    
    #Run Matlab Command
    #-------------------------------------------------------------------
    os.system(cmd)
    #-------------------------------------------------------------------
    
    return None





