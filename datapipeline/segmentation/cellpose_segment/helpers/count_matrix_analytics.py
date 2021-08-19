import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_number_of_genes_per_cell(count_matrix_src):
    
    df_count_matrix = pd.read_csv(count_matrix_src)
    
    df_count_matrix_only_cells = df_count_matrix.drop(columns='gene')
    
    number_of_genes_per_cell = df_count_matrix_only_cells.sum().mean()
    
    return number_of_genes_per_cell

def write_number_of_genes_per_cell_to_file(count_matrix_src, txt_dst):
    
    #Get Number of genes Per Cell
    #================================================
    number_of_genes_per_cell = get_number_of_genes_per_cell(count_matrix_src)
    
    file1 = open(txt_dst,"w")
    file1.write("Number of Genes Per Cell: " + str(round(number_of_genes_per_cell,2)))
    file1.close() #to change file access modes
    
def save_plot_of_number_of_barcodes_per_cell(count_matrix_src, png_dst):
    
    #Get Count Matrix
    #---------------------------------------------------
    df_count_matrix = pd.read_csv(count_matrix_src)
    df_count_matrix_only_cells = df_count_matrix.drop(columns='gene')
    #---------------------------------------------------
    
    #---------------------------------------------------
    plt.figure()
    plt.title('Histogram of Barcodes Per Cell')
    plt.xlabel('Barcodes Per Cell')
    plt.ylabel('Number of Cells')
    plt.hist(df_count_matrix_only_cells.sum())
    plt.savefig(png_dst)
    #---------------------------------------------------

