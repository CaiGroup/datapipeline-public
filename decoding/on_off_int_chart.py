import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import os

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
    