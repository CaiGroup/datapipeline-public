import os
import numpy as np
from scipy.io import loadmat

def get_barcode_info(barcode_src):
    
    #Get Info on how Barcode key is structured
    #-------------------------------------------------------------------
    print("Reading Barcode Key")
    print(f'{barcode_src=}')
    barcodes = loadmat(barcode_src)["barcodekey"]
    num_of_rounds = barcodes[0][0][0].shape[1]
    channels_per_round = np.max(barcodes[0][0][0][:200])
    total_number_of_channels = num_of_rounds*channels_per_round
    #-------------------------------------------------------------------
    
    #Make assertion to double check
    #-------------------------------------------------------------------
    print(f'{total_number_of_channels=}')
    print(f'{num_of_rounds=}')
    assert total_number_of_channels % num_of_rounds == 0
    #-------------------------------------------------------------------
    
    return total_number_of_channels, num_of_rounds

def decoding(barcode_src ,locations_src, dest, allowed_diff, min_seeds, channel_index = None, number_of_individual_channels_for_decoding=None):
    
    #Get Barcode key info
    #-------------------------------------------------------------------
    total_number_of_channels, num_of_rounds = get_barcode_info(barcode_src)
    #-------------------------------------------------------------------
    
    #Get current working directory to put in command
    #-------------------------------------------------------------------
    folder = os.path.dirname(__file__)
    decoding_dir = os.path.join(folder, 'helpers')
    #-------------------------------------------------------------------
    
    
    #Template for commmand
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """
    #-------------------------------------------------------------------
    
    
    #Fill in command based off individual channel or across 
    #-------------------------------------------------------------------
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
    #-------------------------------------------------------------------

    #Run command
    #-------------------------------------------------------------------
    os.system(cmd)
    #-------------------------------------------------------------------
    if min_seeds =='number_of_rounds - 1':
        min_seeds = num_of_rounds - 1
        
    return os.path.join(dest, 'pre_seg_diff_' + str(allowed_diff) + '_minseeds_' + str(min_seeds) + '_unfiltered.csv')

if __name__ == '__main__':

    import sys
    if sys.argv[1] == 'debug_no_parallel':
        dest = 'foo/multi_channels_decoding_test'
        if not os.path.exists(dest):
            os.makedirs(dest)
        decoding(barcode_src = '/groups/CaiLab/analyses/nrezaee/test1-indiv/3d_indiv_all_2_ch/BarcodeKey/channel_2.mat',
                locations_src = '/groups/CaiLab/analyses/nrezaee/test1-indiv/3d_indiv_all_2_ch/MMStack_Pos0/Dot_Locations/locations.csv',
                dest = dest,
                allowed_diff = 1,
                min_seeds = 3,
                channel_index = 1,
                number_of_individual_channels_for_decoding = 2)

