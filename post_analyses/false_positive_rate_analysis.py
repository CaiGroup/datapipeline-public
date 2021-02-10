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

def save_to_file(num_reals, num_fakes, ratio, num_reals_seg, num_fakes_seg, ratio_seg, dst):
    state_reals = 'Number of On Barcodes: ' + str(num_reals)
    state_offs =  'Number of Off Barcodes: ' + str(num_fakes)
    state_ratio = 'False Positive Rate: ' + str(ratio)
    
    state_reals_cells = 'Number of On Barcodes in Cells: ' + str(num_reals_seg)
    state_offs_cells =  'Number of Off Barcodes in Cells: ' + str(num_fakes_seg)
    state_ratio_cells = 'False Positive Rate  in Cells: ' + str(ratio_seg)
    
    file1 = open(dst,"w") 
    L = [state_reals + '\n', \
         state_offs+ '\n', \
         state_ratio, '\n\n', \
         state_reals_cells + '\n', \
         state_offs_cells + '\n', \
         state_ratio_cells]  

    file1.writelines(L) 
    file1.close() 
    
    print("Saving False Barcodes to", dst)
    
def get_false_positive_rate_info(df_genes):

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
    
    df = pd.read_csv(genes_csv_src)
    
    fake_ids = [ gene for gene in df.geneID if 'fake' in gene]
    real_ids = [ gene for gene in df.geneID if 'fake' not in gene]

    df_fake = df[df.geneID.isin(fake_ids)]
    df_real = df[df.geneID.isin(real_ids)]
    

    pop_a = mpatches.Patch(color='b', label='On Barcodes')
    pop_b = mpatches.Patch(color='orange', label='Off Barcodes')
    plt.figure(figsize = (20,10))
    plt.legend(handles=[pop_a,pop_b], prop={'size': 30})
    plt.title('Intensity Analysis Across On/Off Barcodes', fontsize=40)
    plt.hist([df_real.intensity, df_fake.intensity], stacked = True, \
             rwidth=0.8, color = ['b', 'orange'])
    plt.savefig(dest)

def get_false_pos_intensities_hist(genes_csv_src, dest):
    
    df = pd.read_csv(genes_csv_src)
    
    fake_ids = [ gene for gene in df.geneID if 'fake' in gene]
    real_ids = [ gene for gene in df.geneID if 'fake' not in gene]

    df_fake = df[df.geneID.isin(fake_ids)]
    df_real = df[df.geneID.isin(real_ids)]
    

    pop_a = mpatches.Patch(color='b', label='On Barcodes')
    pop_b = mpatches.Patch(color='orange', label='Off Barcodes')
    plt.figure(figsize = (20,10))
    plt.legend(handles=[pop_a,pop_b], prop={'size': 30})
    plt.title('Intensity Analysis Across On/Off Barcodes', fontsize=40)
    plt.hist([df_real.intensity, df_fake.intensity], stacked = True, \
             rwidth=0.8, color = ['b', 'orange'])
    plt.savefig(dest)
    
def get_false_pos_rate_post_seg(gene_locations_assigned_to_cell_src, dst, upto = None):
    print("Getting False Barcodes")
    
    #Get Dataframe
    #=====================================================
    df_genes = pd.read_csv(gene_locations_assigned_to_cell_src)[:upto]
    #=====================================================

    #Get False Positives
    #------------------------------------------------------
    num_fakes, num_reals, ratio = get_false_positive_rate_info(df_genes)
    #------------------------------------------------------
    
    #Remove the Genes outside the cells
    #------------------------------------------------------
    print(f'{df_genes.shape=}')
    df_genes_only_cells = df_genes[df_genes['cellID'] != 0]
    #--------------------------00------------------------------ 
    
    #Get False Positives
    #------------------------------------------------------
    num_fakes_seg, num_reals_seg, ratio_seg = get_false_positive_rate_info(df_genes_only_cells)
    #------------------------------------------------------  
    
    #Write to text file
    #------------------------------------------------------
    save_to_file(num_reals, num_fakes, ratio, num_reals_seg, num_fakes_seg, ratio_seg, dst)
    #------------------------------------------------------
    
    fig_dest = os.path.join(os.path.basename(dst), 'On-Off-Barcode-Intensity-Analysis.png')
    get_false_pos_intensities_hist(gene_locations_assigned_to_cell_src, fig_dest)
    
    print("Saving False Barcodes to", dst)

    return num_reals, num_fakes, ratio
    
    
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

