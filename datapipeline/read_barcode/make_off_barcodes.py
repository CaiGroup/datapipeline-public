import pandas as pd
import random
from itertools import permutations 
from itertools import combinations_with_replacement   
import numpy as np
import sys

def get_all_possible(num_pseudos, code_len):
    """
    Get all possible codewords
    """
    
    # Get Info
    #-------------------------------------------------------
    pseudos = list(range(1, int(num_pseudos) + 1))
    comb = list(combinations_with_replacement(pseudos, code_len))  
    #-------------------------------------------------------
    
    # Get all possible combinations
    #-------------------------------------------------------
    all_possible_bars = []
    for elem in comb:
        perm = permutations(elem)
        for perm_elem in perm:
            all_possible_bars.append(list(perm_elem))
    
    unique_all_bars = np.unique(np.array(all_possible_bars), axis=0)
    #-------------------------------------------------------
    
    return unique_all_bars

def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def get_off_bars(on_barcode, all_barcodes):
    """
    Extract off barcodes from all barcodes
    """
    codes_cols = on_barcode.columns[1:]
    on_bars_minus_genes = on_barcode[codes_cols].values
    off_genes = np.array(Diff(on_bars_minus_genes.tolist(), all_barcodes.tolist()))
    return off_genes

def make_matrix_into_df(off_genes):
    """
    Turns matrix into dataframe
    """
    # Turns Matrix into dict
    #-------------------------------------------------------
    dict_for_df = {}
    for i in range(off_genes.shape[1]):
        dict_for_df["Hyb" + str(i+1)] = np.array(off_genes)[:,i]
    
    df_fake = pd.DataFrame(dict_for_df)
    #-------------------------------------------------------
    
    # Make gene labels of fake + i
    #-------------------------------------------------------
    labels = ['fake']*df_fake.shape[0]
    i=0
    for i in range(len(labels)):
        labels[i] = labels[i] + str(i)
        
    df_fake['gene'] = labels
    df_fake = df_fake[df_fake.columns.insert(0, list(df_fake.columns).pop())[:-1]]
    #-------------------------------------------------------
    
    return df_fake

def get_off_barcodes(barcode_src, off_barcode_dst):
    """
    Takes in a barcode source and then gets the off barcodes of two Hamming Distance
    
    Saves to off_barcode_dst
    """
    
    # Get more info on barcode csv
    #-------------------------------------------------------
    on_barcode = pd.read_csv(barcode_src)
    hyb_cols = [col for col in on_barcode.columns if 'gene' not in col.lower()]
    num_pseudos = max(on_barcode[hyb_cols].max(axis=0))
    num_rounds = on_barcode.shape[1] - 2
    #-------------------------------------------------------
    
    # Only get possible off barcodes
    #-------------------------------------------------------
    all_barcodes = get_all_possible(num_pseudos, num_rounds)
    on_bars_first_3 = on_barcode[on_barcode.columns[:4]]
    off_genes = get_off_bars(on_bars_first_3, all_barcodes)
    #-------------------------------------------------------
    
    # Get the right Hyb4
    #-------------------------------------------------------
    df_off = make_matrix_into_df(off_genes)
    df_off['Hyb4'] = df_off.apply(lambda row: (row.Hyb1 + row.Hyb2 + row.Hyb3)%num_pseudos, axis=1)
    df_off['Hyb4'] = np.where(df_off['Hyb4'] ==0, num_pseudos, df_off['Hyb4'])
    df_off.to_csv(off_barcode_dst, index = False)
    #-------------------------------------------------------
    
    #Change column names
    #-------------------------------------------------------
    df_off.columns = on_barcode.columns
    #-------------------------------------------------------
    
    #Save off barcode
    #-------------------------------------------------------
    df_off.to_csv(off_barcode_dst, index = False)
    #-------------------------------------------------------
    
    return df_off

if __name__ == '__main__':

    if sys.argv[1] == 'debug_get_off':
        src = '/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_9/barcode_key/channel_2.csv'
        dst = 'foo/channel_2_fake.csv'
        get_off_barcodes(src, dst)
        print(f'{dst=}')
    