import os 
import pandas as pd
import random
import numpy as np
import sys
import ast
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def get_random(n=16):
    return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(n))
    
def get_cost_with_on_off(csv_src, png_dst):
    """
    Makes chart comparing the cost of on and off barcodes
    """
    #Separate On/Off
    #---------------------------------------------------------------
    df = pd.read_csv(csv_src)
    fake_ids = [ gene for gene in df.gene if 'fake' in gene]
    real_ids = [ gene for gene in df.gene if 'fake' not in gene]
    df_fake = df[df.gene.isin(fake_ids)]
    df_real = df[df.gene.isin(real_ids)]
    #---------------------------------------------------------------
    
    #Plot Cost for On/Off
    #---------------------------------------------------------------
    plt.figure(figsize=(10,5))
    plt.hist([df_real.cost, df_fake.cost], stacked = True, \
         rwidth=0.8, color = ['b', 'orange'])
    #---------------------------------------------------------------
    
    #Add Labels to plot
    #---------------------------------------------------------------
    plt.title('Plot Cost Across On/Off Genes')
    pop_a = mpatches.Patch(color='b', label='On Barcodes')
    pop_b = mpatches.Patch(color='orange', label='Off Barcodes')
    plt.legend(handles=[pop_a,pop_b], prop={'size': 10})
    plt.xlabel('Cost')
    plt.ylabel('Gene Counts')
    plt.savefig(png_dst)
    #---------------------------------------------------------------

def process_decoding_results(decoded_results_src, barcode_src, dst):
    """
    Add x,y, and z to results
    Replace "value" with gene name
    Save to dst
    """
    
    #Get Average X, Y, and Z
    #---------------------------------------------------------------
    df_new_res = pd.read_csv(decoded_results_src)
    np_x_s = np.array([ast.literal_eval(xs) for xs in df_new_res['xs']])
    df_new_res['x'] = np_x_s.mean(1)
    np_y_s = np.array([ast.literal_eval(ys) for ys in df_new_res['ys']])
    df_new_res['y'] = np_y_s.mean(1)
    np_z_s = np.array([ast.literal_eval(zs) for zs in df_new_res['zs']])
    df_new_res['z'] = np_z_s.mean(1)
    #---------------------------------------------------------------
    
    
    #Add Gene column to results
    #---------------------------------------------------------------
    df_bars = pd.read_csv(barcode_src)
    genes = []
    for gene_index in df_new_res.value:
        print(f'{gene_index=}')
        print(f'{df_bars.shape=}')
        print(f'{df_bars.iloc[gene_index -1]=}')
        print(f'{df_bars.iloc[gene_index -1, 0]=}')
        print(f'{type(df_bars.iloc[gene_index -1, 0])=}')
        genes.append(df_bars.iloc[gene_index -1, 0])
        # genes.append(df_bars.iloc[gene_index -1].gene)
        
    df_new_res['gene'] = genes
    del df_new_res['value']
    #---------------------------------------------------------------
    
    #Save results
    #---------------------------------------------------------------
    df_new_res = df_new_res[['gene', 'x', 'y', 'z', 'cost', 'xs', 'ys', 'cc', 'cc_size']]
    df_new_res.to_csv(dst, index=False)
    #---------------------------------------------------------------
    return df_new_res
    
def process_locations_src(locations_src, barcode_src, locations_dst):
    """
    Change Locations csv file to fit decoding format 
    Save to randomized temp directory
    """
    df_locs = pd.read_csv(locations_src)
    
    #Get right hybs
    #------------------------------------
    df_locs['hyb'] = pd.factorize(df_locs.hyb)[0] + 1
    
    df_bars = pd.read_csv(barcode_src)
    pseudos = np.max(np.array(df_bars.iloc[:,-4:]))
    hybs_for_decoding = list(range(1, int(pseudos)*4 + 1))
    df_locs = df_locs.loc[df_locs['hyb'].isin(hybs_for_decoding)]
    print(f'{hybs_for_decoding=}')
    #------------------------------------
    
    
    #Set s to 1 for now
    #------------------------------------
    df_locs['s'] = 1
    #------------------------------------
    
    #Make small changes
    #------------------------------------
    df_locs_int_to_w = df_locs.rename(columns={"int": "w"})
    del df_locs_int_to_w['ch']
    #------------------------------------
    
    #Save to dst
    #------------------------------------
    dst = os.path.join(locations_dst, 'sim_anneal_locs.csv')
    df_locs_int_to_w.to_csv(locations_dst, index=False)
    print(f'{locations_dst=}')
    #------------------------------------
    
def process_barcode(barcode_src, barcode_dst):
    """
    Change Barcode csv file to fit decoding format
    Save to randomized temp directory
    """
    #Read barcode in 
    #------------------------------------
    df_barcode = pd.read_csv(barcode_src)
    #------------------------------------
    
    #Get Max dataframe
    #------------------------------------
    hyb_cols = df_barcode.columns[-4:]
    max_pseudo = df_barcode[hyb_cols].to_numpy().max()
    #------------------------------------
    
    #Change max pseudo to zero
    #------------------------------------
    for hyb_col in hyb_cols:
        df_barcode[hyb_col] = np.where((df_barcode[hyb_col] == max_pseudo), 0, df_barcode[hyb_col])
    df_barcode[hyb_cols].astype(np.int8).to_csv(barcode_dst, sep='\t', index=False, header=False)
    print(f'{barcode_dst=}')
    #------------------------------------
    
def combine_with_fake(barcode_src, temp_dir):
    """
    Combine ON and off barcodes
    Save to dst
    """
    
    #Load On and Off Barcode
    #---------------------------------------------------------------
    fake_barcode_src = os.path.join(os.path.dirname(barcode_src), os.path.basename(barcode_src).split('.csv')[0] + '_fake.csv')
    df_bars = pd.read_csv(barcode_src)
    df_fake_bars = pd.read_csv(fake_barcode_src)
    #---------------------------------------------------------------
    
    #Combine and save to temp dir
    #---------------------------------------------------------------
    df_all_bars = df_bars.append(df_fake_bars)
    on_and_off_barcode_src = os.path.join(temp_dir, 'barcode.csv')
    print(f'{on_and_off_barcode_src=}')
    df_all_bars.to_csv(on_and_off_barcode_src, index=False)
    #---------------------------------------------------------------
    
    return on_and_off_barcode_src
    

def run_syndrome_decoding(locations_src, barcode_src, dst_dir, bool_fake_barcodes, lat_var_factor=112, z_var_factor=0, lw_var_factor=4):
    """
    Format barcode csv and locations csv to fit decoding formats
    Save results to a directory once finished
    """
    
    #Make temp dir
    #---------------------------------------------------------------
    temp_dir = os.path.join('/groups/CaiLab/personal/temp/temp_decode', get_random())
    os.mkdir(temp_dir)
    #---------------------------------------------------------------
    
    #Save locations
    #---------------------------------------------------------------
    locs_path = os.path.join(temp_dir, 'locs_for_sim_anneal.csv')
    process_locations_src(locations_src, barcode_src, locs_path)
    #---------------------------------------------------------------
    
    
    #Save barcode for Syndrome decoding
    #---------------------------------------------------------------
    if bool_fake_barcodes:
        print(f'{barcode_src=}')
        barcode_src = combine_with_fake(barcode_src, temp_dir)
    barcode_path = os.path.join(temp_dir, 'codewords_for_sim_anneal.txt')
    process_barcode(barcode_src, barcode_path)
    #---------------------------------------------------------------
    
    
    #Run julia code for syndrome decoding
    #---------------------------------------------------------------
    julia_script_path = os.path.join(os.getcwd(), 'decoding', 'syndrome_helpers', 'decode.jl')
    cmd = 'julia '+ julia_script_path + ' ' + locs_path + ' ' + barcode_path + ' ' + dst_dir + \
            ' ' + str(lat_var_factor) + ' ' + str(z_var_factor) + ' ' + str(lw_var_factor)
    print(f'{cmd=}')
    os.system(cmd)
    #---------------------------------------------------------------
    
    #Save results
    #---------------------------------------------------------------
    results_csv = os.path.join(dst_dir, 'mpaths_decode_w_neg_ctrl_lvf112.0_lwvf4.0dr0.csv')
    processed_results_csv = os.path.join(dst_dir, 'pre_seg_unfiltered.csv')
    process_decoding_results(results_csv, barcode_src, processed_results_csv)
    print(f'{processed_results_csv=}')
    #---------------------------------------------------------------
    
    #See On/Off cost analytics
    #---------------------------------------------------------------
    dst_cost_analysis = os.path.join(dst_dir, 'On_Off_Cost_Analysis.png')
    get_cost_with_on_off(processed_results_csv, dst_cost_analysis)
    #---------------------------------------------------------------
    
    
#Test
if sys.argv[1] == 'debug_synd_decoding':
    barcode_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/barcode_key/channel_1.csv'
    locations_src = '/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/MMStack_Pos0/Dot_Locations/locations.csv'
    dst_dir = 'foo'
    bool_fake_barcodes = True
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
        
    run_syndrome_decoding(locations_src, barcode_src, dst_dir, bool_fake_barcodes)

elif sys.argv[1] == 'debug_fake_barcodes':
    barcode_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/barcode_key/channel_1.csv'
    temp_dir = 'foo/make_fake_barcodes'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    combine_with_fake(barcode_src, temp_dir)
        
elif sys.argv[1] == 'debug_synd_anthony':
    barcode_src = '/groups/CaiLab/personal/nrezaee/raw/anthony_0512_2021/barcode_key/channel_2.csv'
    locations_src = '/groups/CaiLab/analyses/nrezaee/anthony_0512_2021/anthony_strict_35_synd_pos0/MMStack_Pos10/Dot_Locations/locations.csv'
    dst_dir = 'foo'
    bool_fake_barcodes = True
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
        
    run_syndrome_decoding(locations_src, barcode_src, dst_dir, bool_fake_barcodes)
    
elif sys.argv[1] == 'debug_process_locs':
    barcode_src = '/groups/CaiLab/personal/nrezaee/raw/anthony_0512_2021/barcode_key/channel_2.csv'
    locations_src = '/groups/CaiLab/analyses/nrezaee/anthony_0512_2021/anthony_strict_35_synd_pos0/MMStack_Pos10/Dot_Locations/locations.csv'
    locations_dst = 'foo/locs.csv'
    process_locations_src(locations_src, barcode_src, locations_dst)

elif sys.argv[1] == 'debug_process_results':
    results_src = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6_synd_pos0/MMStack_Pos0/Decoded/Channel_1/mpaths_decode_w_neg_ctrl_lvf112.0_lwvf4.0dr0.csv'
    barcode_src = '/groups/CaiLab/personal/temp/temp_decode/3FSG69S11UXMR2EM/barcode.csv'
    dst = 'foo/results.csv'
    process_decoding_results(results_src, barcode_src, dst)
    
    
    
    
    
    
    
    
    
    
    
    