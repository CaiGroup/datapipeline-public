import pandas as pd 
import glob
import os
import sys

def comb_decoded_csv(df_all_genes, csv, channel):
    
    df_add_me = pd.read_csv(csv)
    if channel != None:
        df_add_me['ch'] = channel
    df_add_me['pos'] = int(csv.split('MMStack_Pos')[1].split('/Decoded')[0])
    print(f'{df_add_me.shape=}')
    df_all_genes = df_all_genes.append(df_add_me)
    
    return df_all_genes
    
def combine_pos_genes(analysis_dir, channel=None):

    #Get Decoded Genes
    dest = os.path.join(analysis_dir, 'Decoded_Genes.csv')
    if channel != None:
        glob_me = os.path.join(analysis_dir, 'MMStack_Pos*','Decoded', 'Channel_' +str(channel), '*unfiltered.csv')
    decoded_csv_s = glob.glob(glob_me)
    
    #Combine all csv_s
    df_all = pd.read_csv(decoded_csv_s[0])
    print(f'{df_all.shape=}')
    for csv in decoded_csv_s[1:]:
        df_all = comb_decoded_csv(df_all, csv, channel)
        print(f'{df_all.shape=}')
    
    #Save all decoded genes combined
    df_all_pos_dst = os.path.join(analysis_dir, 'All_Positions', 'Decoded', 'all_pos_decoded_genes_unfiltered.csv')
    os.makedirs(os.path.dirname(df_all_pos_dst), exist_ok=True)
    print(f'{df_all_pos_dst=}')
    df_all.to_csv(df_all_pos_dst, index=False)
    
    

if sys.argv[1] == 'debug_comb_genes':
    analysis_dir = '/groups/CaiLab/analyses/michalp/michal_2/michal_2_decoding_test/'
    channel = 1
    combine_pos_genes(analysis_dir, channel)
    
    
    






