import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def get_on_off_barcode_plot(gene_locations_assigned_to_cell_src, dst_dir):
    
    df_genes = pd.read_csv(gene_locations_assigned_to_cell_src)

    #Remove the Genes outside the cells
    #------------------------------------------------------
    df_genes_only_cells = df_genes[df_genes['cellID'] != 0]
    #------------------------------------------------------


    #Get the Gene counts for Reals and fakes
    #------------------------------------------------------
    gene_counts = df_genes_only_cells.gene.value_counts()
    dict_gene_counts = dict(gene_counts)

    real_counts = []
    fake_counts = []
    for key in dict_gene_counts.keys():
        if 'fake' in key:
            fake_counts.append(dict_gene_counts[key])
        else:
            real_counts.append(dict_gene_counts[key])
    #------------------------------------------------------

    #Plot the figure
    #------------------------------------------------------
    plt.figure(figsize=(8,6))

    plt.title('On/Off Sorted Barcode Counts', fontsize = 23)

    num_cells = 1

    plt.ylabel('Counts of Genes', fontsize=18)
    plt.xlabel('Sorted Barcodes', fontsize=18)
    plt.plot(np.array(real_counts)/num_cells)
    x_points_for_fake = range(len(real_counts), len(real_counts)+len(fake_counts))
    plt.plot(x_points_for_fake, np.array(fake_counts))
    
    on_off_barcode_plot_dst = os.path.join(dst_dir, 'On_Off_Sorted_Barcode_Plot.png')
    plt.savefig(on_off_barcode_plot_dst)
    #------------------------------------------------------
    
def get_on_off_barcode_plot_pre_seg(gene_locations_assigned_to_cell_src, dst_dir):
    
    df_genes = pd.read_csv(gene_locations_assigned_to_cell_src)

    #Remove the Genes outside the cells
    #------------------------------------------------------
    df_genes_only_cells = df_genes[df_genes['cellID'] != 0]
    #------------------------------------------------------


    #Get the Gene counts for Reals and fakes
    #------------------------------------------------------
    gene_counts = df_genes_only_cells.gene.value_counts()
    dict_gene_counts = dict(gene_counts)

    real_counts = []
    fake_counts = []
    for key in dict_gene_counts.keys():
        if 'fake' in key:
            fake_counts.append(dict_gene_counts[key])
        else:
            real_counts.append(dict_gene_counts[key])
    #------------------------------------------------------

    #Plot the figure
    #------------------------------------------------------
    plt.figure(figsize=(8,6))

    plt.title('On/Off Sorted Barcode Counts', fontsize = 23)

    num_cells = 1

    plt.ylabel('Counts of Genes', fontsize=18)
    plt.xlabel('Sorted Barcodes', fontsize=18)
    plt.plot(np.array(real_counts)/num_cells)
    x_points_for_fake = range(len(real_counts), len(real_counts)+len(fake_counts))
    plt.plot(x_points_for_fake, np.array(fake_counts))
    
    on_off_barcode_plot_dst = os.path.join(dst_dir, 'On_Off_Sorted_Barcode_Plot.png')
    plt.savefig(on_off_barcode_plot_dst)
    #------------------------------------------------------