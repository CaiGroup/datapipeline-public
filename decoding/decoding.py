import os
import numpy as np
from scipy.io import loadmat

def get_barcode_info(barcode_src):

    print("Reading Barcode Key")
    
    barcodes = loadmat(barcode_src)["barcodekey"]

    num_of_rounds = barcodes[0][0][0].shape[1]
    
    channels_per_round = np.max(barcodes[0][0][0][:200])
    
    total_number_of_channels = num_of_rounds*channels_per_round
    
    assert total_number_of_channels % num_of_rounds == 0
    
    return total_number_of_channels, num_of_rounds

def decoding(barcode_src ,locations_src, dest, allowed_diff, min_seeds, channel_index = None, number_of_individual_channels_for_decoding=None):
    
    total_number_of_channels, num_of_rounds = get_barcode_info(barcode_src)
    
    cwd = os.getcwd()
    cwd = cwd[cwd.find('/home'):]
    print(f'{cwd=}')
    decoding_dir = os.path.join(cwd, 'decoding', 'helpers')
    
    cmd = """  matlab -r "addpath('{0}');main_decoding('{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, '{9}'); quit"; """
    
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
        

    os.system(cmd)

    return None
    
import sys
if sys.argv[1] == 'debug_no_parallel':
    barcode_src = '/groups/CaiLab/analyses/nrezaee/linus_data/linus_pos0/BarcodeKey/channel_1.mat'
    locations_src = '/groups/CaiLab/personal/nrezaee/raw/jonathan_linus_analysis/jonathan_dots.csv'
    allowed_diff =1
    min_seeds = 3
    channel_index = None
    number_of_individual_channels_for_decoding = None
    dest = 'foo/jonathan_linus_results'
    if not os.path.exists(dest):
        os.makedirs(dest)
    decoding(barcode_src, locations_src, dest, allowed_diff, min_seeds, channel_index, number_of_individual_channels_for_decoding)
    





