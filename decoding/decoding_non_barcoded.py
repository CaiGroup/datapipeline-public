import pandas as pd
import numpy as np
import sys
import os

def locations_to_gene(df_codes, df_locs, position):
    
    genes_to_locs = []
    
    #Match genes to hybs and channels
    #--------------------------------------------------
    for hyb in df_codes.hyb.unique():
        for ch in df_codes.channel.unique():
            
            #Get Gene
            gene = df_codes[(df_codes.hyb == hyb) & \
                            (df_codes.channel == ch)]
                            
            #See if gene is present and add
            if len(gene) > 0:
                df_locs.loc[(df_locs.hyb == hyb) & \
                            (df_locs.ch ==ch), 'gene'] = gene.iloc[0,0]
                
    return df_locs

def run_decoding_non_barcoded(sequential_csv, locations_csv, position, dst_dir):
    
    #Read Barcodes and locations
    #--------------------------------------------------
    df_codes = pd.read_csv(sequential_csv)
    df_locs = pd.read_csv(locations_csv)
    #--------------------------------------------------
    
    #Get Genes from dots
    #--------------------------------------------------
    df_locs["gene"] = np.nan
    df_decoded = locations_to_gene(df_codes, df_locs, position)
    #--------------------------------------------------
    
    #Save Decoded Genes
    #--------------------------------------------------
    df_decoded.to_csv(os.path.join(dst_dir, 'sequential_decoding_results.csv'), index= False)
    #--------------------------------------------------
    
    return df_decoded
    
if sys.argv[1] == 'debug_smfish_decoding':
    df_decoded =run_decoding_non_barcoded(sequential_csv = '/groups/CaiLab/personal/nrezaee/raw/test1-big/non_barcoded_genes/sequential_key.csv',
                                 locations_csv = '/groups/CaiLab/analyses/nrezaee/test1-big/non_barcoded/MMStack_Pos0/Dot_Locations/locations.csv',
                                 position = 0,
                                 dst_dir = 'foo')
                                 
    print(f'{df_decoded.gene.head()=}')
                                                                                    
