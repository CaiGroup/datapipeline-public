import pandas as pd
import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(color_codes=True)
import os
import sys


def get_gene_to_gene_correlations(count_matrix_src, dst_dir):
    
    os.makedirs(dst_dir, exist_ok = True)

    df_count_matrix = pd.read_csv(count_matrix_src)

    #Remove fake gene names
    #--------------------------------------------------
    real_ids = [gene_id for gene_id in df_count_matrix['gene'] if 'fake' not in gene_id]
    df_count_matrix = df_count_matrix[df_count_matrix['gene'].isin(real_ids)]
    #--------------------------------------------------

    #Filter out bottome 10% of cells
    #--------------------------------------------------
    percentile_to_be_removed = .05
    thresh_of_number_of_genes_per_cell = df_count_matrix.iloc[:,1:].sum(axis=0).quantile(percentile_to_be_removed)

    df_count_matrix = df_count_matrix[pd.Series(df_count_matrix.iloc[:,1:].sum() > thresh_of_number_of_genes_per_cell).index]
    #--------------------------------------------------

    #Normalize for each cell
    #--------------------------------------------------
    for column in df_count_matrix.columns:
        big_sum = df_count_matrix[column].sum()
        df_count_matrix[column] = (df_count_matrix[column] / big_sum)*1000
    #--------------------------------------------------

    #Remove NA's
    #--------------------------------------------------
    df_count_matrix.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_count_matrix = df_count_matrix.dropna(axis='columns')
    #--------------------------------------------------

    #Get Correlations
    #--------------------------------------------------
    corr_matrix = df_count_matrix.values
    corr_matrix = 1 - sklearn.metrics.pairwise_distances(corr_matrix, metric='correlation')
    #--------------------------------------------------


    #Get Unclustered Correlation Matrix
    #--------------------------------------------------
    unclustered_corr_plot_dst = os.path.join(dst_dir, 'unclustered_corr_plot.png')
    plt.figure(figsize=(12,12))
    plt.imshow(corr_matrix, cmap='gray')
    plt.colorbar()
    plt.savefig(unclustered_corr_plot_dst)
    print(f'{unclustered_corr_plot_dst=}')
    #--------------------------------------------------


    #Get Clustered 
    #--------------------------------------------------
    clustered_corr_plot_dst = os.path.join(dst_dir, 'clustered_corr_plot.png')
    sns_cluster = sns.clustermap(corr_matrix, metric='canberra')
    sns_cluster.savefig(clustered_corr_plot_dst)
    print(f'{clustered_corr_plot_dst=}')
    #--------------------------------------------------

if sys.argv[1] == 'debug_corr_matrix_plot':
    count_matrix_src = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_strict_2_tophat_again/All_Positions/Segmentation/count_matrix_all_pos.csv'
    dst_dir = 'foo/corr_matrix'
    os.makedirs(dst_dir, exist_ok = True)
    get_gene_to_gene_correlations(count_matrix_src, dst_dir)