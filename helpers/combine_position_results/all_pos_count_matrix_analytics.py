import os
import glob
import matplotlib.pyplot as plt
import pandas as pd
import sys

def get_number_of_genes_per_cell(count_matrix_src):
    
    df_count_matrix = pd.read_csv(count_matrix_src)
    
    df_count_matrix_only_cells = df_count_matrix.drop(columns='gene')
    
    number_of_genes_per_cell = df_count_matrix_only_cells.sum().mean()
    
    return number_of_genes_per_cell
    
def get_plot_from_count_matrix_dict(all_pos_genes_per_cell, dst):
    
    #Make Plot
    #------------------------------------------------
    plt.figure()
    plt.title('Genes Per Cell For Every Position and Channel')
    plt.ylabel('Genes Per Cell')
    plt.grid(axis="y")
    
    plt.bar(range(len(all_pos_genes_per_cell)), list(all_pos_genes_per_cell.values()), align='center')
    plt.xticks(range(len(all_pos_genes_per_cell)), list(all_pos_genes_per_cell.keys()), rotation='vertical', fontsize=10)
    plt.tight_layout()
    plt.savefig(dst)
    #------------------------------------------------ 

def get_number_of_genes_per_cell_dict(count_matrix_src_s):
    
    #Get Number of Genes per cell for each count matrix
    #---------------------------------------------------------
    all_pos_genes_per_cell = {}
    for count_matrix_src in count_matrix_src_s:
        if 'Channel' in count_matrix_src:
            pos = count_matrix_src.split(os.sep)[7]
            channel = count_matrix_src.split(os.sep)[9]
            key = pos + ' ' + channel
        else:
            pos = count_matrix_src.split(os.sep)[7]
            key = pos
        
        all_pos_genes_per_cell[key] = get_number_of_genes_per_cell(count_matrix_src)
    #---------------------------------------------------------
        
    return all_pos_genes_per_cell

def get_all_count_matrix_src_s(analysis_dir):
    
    #Get all count matrices-
    #---------------------------------------------------------
    glob_me_for_count_matrics_indiv = os.path.join(analysis_dir,'MMStack_Pos*', 'Segmentation', 'Channel*', 'count_matrix.csv')
    glob_me_for_count_matrics_across = os.path.join(analysis_dir, 'MMStack_Pos*', 'Segmentation', 'count_matrix.csv')
    
    count_matrices_indiv = glob.glob(glob_me_for_count_matrics_indiv)
    count_matrices_across = glob.glob(glob_me_for_count_matrics_across)
    
    count_matrix_src_s = count_matrices_indiv + count_matrices_across
    print(f'{len(count_matrix_src_s)=}')
    #---------------------------------------------------------
    
    return count_matrix_src_s
    
def get_genes_per_cell_for_all_pos_plot(analysis_dir, dst):
    
    os.makedirs(os.path.dirname(dst), exist_ok = True)
    
    #Get all count matrices from analysis dir
    #---------------------------------------------------------
    count_matrix_src_s  = get_all_count_matrix_src_s(analysis_dir)
    #---------------------------------------------------------
    
    #Get count matrix dict
    #---------------------------------------------------------
    all_pos_genes_per_cell = get_number_of_genes_per_cell_dict(count_matrix_src_s)
    #---------------------------------------------------------
    
    #Get plot from gener per cell dict
    #---------------------------------------------------------
    get_plot_from_count_matrix_dict(all_pos_genes_per_cell, dst)
    print(f'{dst=}')
    #---------------------------------------------------------
 
if sys.argv[1] == 'debug_jina_pseudos_4_strict_0':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot'
    dst = 'jina_pseudos_4_strict_0.png'
    
    get_genes_per_cell_for_all_pos_plot(analysis_dir, dst)
    
if sys.argv[1] == 'debug_jina_pseudos_4_strict_1':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot_strict_1'
    dst = 'jina_pseudos_4_strict_1.png'
    
    get_genes_per_cell_for_all_pos_plot(analysis_dir, dst)

if sys.argv[1] == 'debug_jina_pseudos_4_strict_2':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot_strict_2'
    dst = 'jina_pseudos_4_strict_2.png'
    
    get_genes_per_cell_for_all_pos_plot(analysis_dir, dst)
