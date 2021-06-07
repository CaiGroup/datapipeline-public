import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import os



#Get Amount of Real and Fake
#------------------------------------------------------
def get_amount_real_and_fake(mapped_genes):

    fakes = np.array([mapped_gene for mapped_gene in mapped_genes \
                             if mapped_gene['real'] == False])
    reals = np.array([mapped_gene for mapped_gene in mapped_genes \
                         if mapped_gene['real'] != False])

    if (len(reals) + len(fakes)) == 0:
        ratio = 0
    else:
        ratio = len(fakes)/(len(reals) +len(fakes))

    return len(reals), len(fakes), ratio 
#------------------------------------------------------

#Get Mapped Genes
#------------------------------------------------------
def get_mapped_genes(df_genes_only_cells):
    mapped_genes = []
    for index, row in df_genes_only_cells.iterrows():
        
        if 'fake' in row['gene']:
            real = False
        else:
            real =True
        mapped_genes.append({'x': row['x'], 'y':row['y'], 'z':row['z'], 'real':real})

    return mapped_genes
#------------------------------------------------------

def save_to_file(num_reals, num_fakes, ratio, num_reals_seg, num_fakes_seg, \
                 ratio_seg, norm_ratio, dst):
                     
    #Make Statements
    #-----------------------------------------------------------------------------
    state_reals = 'Number of On Barcodes: ' + str(num_reals)
    state_offs =  'Number of Off Barcodes: ' + str(num_fakes)
    state_ratio = 'False Positive Rate: ' + str(ratio)
    
    state_reals_cells = 'Number of On Barcodes in Cells: ' + str(num_reals_seg)
    state_offs_cells =  'Number of Off Barcodes in Cells: ' + str(num_fakes_seg)
    state_ratio_cells = 'False Positive Rate  in Cells: ' + str(ratio_seg)
    
    norm_false_pos = ratio_seg*norm_ratio
    
    state_normalized = 'Normalized False Positive Rate in Cells: ' + str(norm_false_pos)
    #-----------------------------------------------------------------------------
    
    #Write to File
    #-----------------------------------------------------------------------------
    file1 = open(dst,"w") 
    # L = [state_reals + '\n', \
    #      state_offs+ '\n', \
    #      state_ratio, '\n\n', \
    L =  [      state_reals_cells + '\n', \
         state_offs_cells + '\n', \
         state_ratio_cells+ '\n\n',
         state_normalized + '\n\n']  

    file1.writelines(L) 
    file1.close() 
    #-----------------------------------------------------------------------------
    
    print("Saving False Barcodes to", dst)
    
def get_false_positive_rate_info(df_genes):
    """
    Takes in dataframe of genes
    
    Returns the Number of Offs, Ons, and False positive rate
    """
    
    if 'geneID' in df_genes.columns:
        df_genes.rename(columns = {'geneID':'gene'}, inplace=True)
    
    num_fakes = len([gene for gene in df_genes.gene if 'fake' in gene])
    num_reals = len([gene for gene in df_genes.gene if 'fake' not in gene])
    
    if len(df_genes.gene) == 0:
        ratio = 0
    else:
        ratio = num_fakes/len(df_genes.gene)
    return num_fakes, num_reals, ratio
    

def get_false_pos_intensities_hist(genes_csv_src, dest):
    
    #Read in genes df
    #------------------------------------------------------
    df = pd.read_csv(genes_csv_src)
    #------------------------------------------------------

    #Separate Real and Fake ID's
    #------------------------------------------------------
    fake_ids = [ gene for gene in df.gene if 'fake' in gene]
    real_ids = [ gene for gene in df.gene if 'fake' not in gene]

    df_fake = df[df.gene.isin(fake_ids)]
    df_real = df[df.gene.isin(real_ids)]
    #------------------------------------------------------

    #Plot On Off Barcodes Across Intensities
    #------------------------------------------------------
    pop_a = mpatches.Patch(color='b', label='On Barcodes')
    pop_b = mpatches.Patch(color='orange', label='Off Barcodes')
    plt.figure(figsize = (20,10))
    plt.legend(handles=[pop_a,pop_b], prop={'size': 30})
    plt.title('Intensity Analysis Across On/Off Barcodes', fontsize=40)
    y, x, patches = plt.hist([df_real.intensity, df_fake.intensity], stacked = True, \
             rwidth=0.8, color = ['b', 'orange'])
    #------------------------------------------------------


    #Plot the false positive rate for each bar on the bar chart
    #------------------------------------------------------
    for i in range(len(x)-1):
        
        #Get false positive rate
        #------------------------------------------------------
        df_threshed = df[df.intensity > x[i]]
        fake_ids = [ gene for gene in df_threshed.gene if 'fake' in gene]
        df_fake = df_threshed[df_threshed.gene.isin(fake_ids)]
        false_pos_rate = round(df_fake.shape[0]/df_threshed.shape[0], 3)
        #------------------------------------------------------
        
        #PLot it
        #------------------------------------------------------
        plt.text(x[i], y[1][i], str(false_pos_rate), fontsize=25)
        #------------------------------------------------------
    #------------------------------------------------------
    
    #Save bar chart to destination
    #------------------------------------------------------
    plt.savefig(dest)
    print(f'{dest=}')
    #------------------------------------------------------
    
def save_to_file_z(num_reals, num_fakes, ratio, z, dst):
    
    #Make statements for false positive
    #------------------------------------------------------
    state_z = 'Z Slice ' + str(z) + ':'
    state_reals = 'Number of On Barcodes: ' + str(num_reals)
    state_offs =  'Number of Off Barcodes: ' + str(num_fakes)
    state_ratio = 'False Positive Rate: ' + str(ratio)
    #------------------------------------------------------

    #Write to file
    #------------------------------------------------------
    file1 = open(dst,"a") 
    L = [state_z + '\n', \
         state_reals + '\n', \
         state_offs+ '\n', \
         state_ratio, '\n\n']  

    file1.writelines(L) 
    file1.close() 
    #------------------------------------------------------
    print("Saving False Barcodes to", dst)

def false_pos_rate_across_z(df, dst):
    
    #Loop through Z's for false positive rate
    #------------------------------------------------------
    z_s = range(round(min(df.z)), round(max(df.z))+1)
    for z in z_s:
        print(z)
        df_z = df[(df.z > (z-.5)) & (df.z <= (z +.5))]
        num_fakes_z, num_reals_z, ratio_z = get_false_positive_rate_info(df_z)
        save_to_file_z(num_reals_z, num_fakes_z, ratio_z, z, dst)
    #------------------------------------------------------
    
def get_off_on_visuals(decoded_genes_src, dst):
    """
    Input:
        gene_locations_assigned_to_cell.csv
        dst
    
    Output:
        Save png file with visuals of on and off
    
    """
    #Read csv file and get real and fake ids
    #------------------------------------------------------
    df = pd.read_csv(decoded_genes_src)
    fake_ids = [ gene for gene in df.gene if 'fake' in gene]
    real_ids = [ gene for gene in df.gene if 'fake' not in gene]
    #------------------------------------------------------
    
    #Get fake and real df's
    #------------------------------------------------------
    df_fake = df[df.gene.isin(fake_ids)]
    df_real = df[df.gene.isin(real_ids)]
    #------------------------------------------------------
    
    #Plot fakes and real's
    #------------------------------------------------------
    plt.figure(figsize=(30,30))
    plt.scatter(df_fake.x, df_fake.y, s=1, color='red')
    plt.scatter(df_real.x, df_real.y, s=.3, color='blue')
    plt.savefig(dst)
    
        
def get_false_pos_rate_post_seg(gene_locations_assigned_to_cell_src, on_barcode_src, off_barcode_src, dst, upto = None):
    
    #Get normalizing ratio
    #------------------------------------------------------
    on_barcode_shape = pd.read_csv(on_barcode_src).shape[0] - 1
    off_barcode_shape = pd.read_csv(off_barcode_src).shape[0] - 1
    
    norm_ratio = on_barcode_shape/off_barcode_shape
    #------------------------------------------------------
    
    print("Getting False Barcodes")

    #Get Dataframe
    #=====================================================
    df_genes = pd.read_csv(gene_locations_assigned_to_cell_src)[:upto]
    #=====================================================
    print(f'{df_genes=}')
    
    
    #Get False Positives
    #------------------------------------------------------
    num_fakes, num_reals, ratio = get_false_positive_rate_info(df_genes)
    #------------------------------------------------------
    
    #Remove the Genes outside the cells
    #------------------------------------------------------
    print(f'{df_genes.shape=}')
    # df_genes = df_genes[df_genes['cellID'] != 0]
    #--------------------------00------------------------------ 
    
    #Get False Positives
    #------------------------------------------------------
    num_fakes_seg, num_reals_seg, ratio_seg = get_false_positive_rate_info(df_genes)
    #------------------------------------------------------  
    
    #Write to text file
    #------------------------------------------------------
    save_to_file(num_reals, num_fakes, ratio, num_reals_seg, num_fakes_seg, \
                 ratio_seg, norm_ratio, dst)
    #------------------------------------------------------
    
    #Get On/Off Barcodes across intensities
    #------------------------------------------------------
    fig_dest = os.path.join(os.path.dirname(dst), 'On-Off-Barcode-Intensity-Analysis.png')
    get_false_pos_intensities_hist(gene_locations_assigned_to_cell_src, fig_dest)
    #------------------------------------------------------
    
    #Get False Positive Rate Across Z
    #------------------------------------------------------
    false_pos_rate_across_z(df_genes, dst)
    #------------------------------------------------------
    
    #Visuals of On/Off Barcodes
    #------------------------------------------------------
    fig_dest = os.path.join(os.path.dirname(dst), 'Visualize_On_Off_Genes.png')
    get_off_on_visuals(gene_locations_assigned_to_cell_src, fig_dest)
    #------------------------------------------------------
    
    print("Saving False Barcodes to", dst)

    return num_reals, num_fakes, ratio
    
    
import sys
if sys.argv[1] == 'debug_false_pos':
    results_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_mult_ch/MMStack_Pos0/Segmentation/Channel_2/gene_locations_assigned_to_cell.csv'
    dst = '/home/nrezaee/temp/false_pos.txt'
    on_barcode_src = '/groups/CaiLab/personal/Michal/raw/2021-05-20_P4P5P7_282plex_Neuro4196_5/barcode_key/channel_1.csv'
    off_barcode_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_mult_ch/BarcodeKey/channel_1_fake.csv'
    get_false_pos_rate_post_seg(results_src, on_barcode_src, off_barcode_src, dst)
    
    
    
    
    
def get_false_pos_rate_pre_seg(csv_src, barcode_src, dst):
    #Get False Positive
    #--------------------------------------------------
    df_results = pd.read_csv(csv_src)
    df_barcodes = pd.read_csv(barcode_src)
    df_results = pd.read_csv(csv_src)
    df_ons = df_results[df_results.geneID < df_barcodes.shape[0]]
    df_offs = df_results[df_results.geneID > df_barcodes.shape[0]]
    
    false_pos_rate = df_offs.shape[0]/df_results.shape[0]
    num_on_barcodes = df_ons.shape[0]
    num_off_barcodes = df_offs.shape[0]
    #--------------------------------------------------
    
    #Save False POsitives
    #--------------------------------------------------
    state_reals = 'Number of On Barcodes: ' + str(num_on_barcodes)
    state_offs =  'Number of Off Barcodes: ' + str(num_off_barcodes)
    state_ratio = 'False Positive Rate: ' + str(false_pos_rate)
    
    file1 = open(dst,"w") 
    L = [state_reals + '\n', \
         state_offs+ '\n', \
         state_ratio]  

    file1.writelines(L) 
    file1.close() 
    
    print("Saving False Barcodes to", dst)
    #--------------------------------------------------
    
    return false_pos_rate, num_on_barcodes, num_off_barcodes

