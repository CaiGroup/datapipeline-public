import pandas as pd
from statistics import mean
import numpy as np
import os

def hamming_distance(chaine1, chaine2):
    return sum(c1 != c2 for c1, c2 in zip(chaine1, chaine2))

def get_codes_in_list(df_real, barcodes): 
    real_ids = df_real.gene.unique()
    real_codebook = []
    for real_id in real_ids:
        index_of_id = list(barcodes.gene).index(real_id)
        #print(index_of_id)
        real_codebook.append(list(barcodes.iloc[index_of_id][2:]))
    return real_codebook

def get_hamming_distance_of_lists(real_codebook, fake_codebook):
    all_distances = []
    i=0
    for fake_code in fake_codebook:
        print(f'{i=}')
        i+=1
        distances = []
        for real_code in real_codebook:

            ham_dist = hamming_distance(fake_code, real_code)/4
            #print(fake_code, real_code, ham_dist)
            distances.append(ham_dist)
        all_distances.append(min(distances))
        
    return np.array(all_distances)


def get_hamming_analysis(gene_locations_assigned_to_cell_src, barcode_src, dest):
    
    #Get the Segmented Genes
    #---------------------------------------------------------------------
    genes_non_segmented = pd.read_csv(gene_locations_assigned_to_cell_src)
    genes = genes_non_segmented[genes_non_segmented.cellID != 0]
    #---------------------------------------------------------------------
    
    #Separate Real and Fake Genes
    #---------------------------------------------------------------------
    fake_ids = [ gene for gene in genes.gene if 'fake' in gene]
    real_ids = [ gene for gene in genes.gene if 'fake' not in gene]
    
    df_fake = genes[genes.gene.isin(fake_ids)]
    df_real = genes[genes.gene.isin(real_ids)]
    #---------------------------------------------------------------------
    
    #Load the On and Off Barcodes
    #---------------------------------------------------------------------
    on_barcode_src = os.path.join(barcode_src)
    barcode_dir = os.path.dirname(on_barcode_src)
    off_barcode_src = os.path.join(barcode_dir, 'fake_barcode.csv')
    
    on_barcodes = pd.read_csv(on_barcode_src)
    off_barcodes = pd.read_csv(off_barcode_src)

    frames = [on_barcodes, off_barcodes]
    barcodes = pd.concat(frames).reset_index()
    #---------------------------------------------------------------------
    
    #Get the Barcodes in a List 
    #---------------------------------------------------------------------
    real_codebook = get_codes_in_list(df_real, barcodes)
    fake_codebook = get_codes_in_list(df_fake, barcodes)
    #---------------------------------------------------------------------
    
    #Get Hamming Distance
    #---------------------------------------------------------------------
    all_distances = get_hamming_distance_of_lists(real_codebook, fake_codebook)
    #---------------------------------------------------------------------
    

    state_mean = 'Mean of Hamming Distances: ' + str(np.mean(all_distances))
    
    unique, counts = np.unique(all_distances, return_counts=True)
    dict_counts_hamming = dict(zip(unique, counts)) 
    state_counts=  'Counts of Hamming Distances: ' + str(dict_counts_hamming)
    
    file1 = open(dest,"w") 
    L = [state_mean + '\n', \
         state_counts]  
    file1.writelines(L) 
    file1.close() 
    
# gene_locations_assigned_to_cell_src = "data/gene_locations_assigned_to_cell_diff_1_all_rounds.csv"
# barcode_dir = 'data'
# dest = 'results/hamming_analysis.txt'

# get_average_hamming_off_barcodes(gene_locations_assigned_to_cell_src, barcode_dir, dest)
    
    