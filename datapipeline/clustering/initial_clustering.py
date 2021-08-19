import pandas as pd
import os
import re
from scipy import stats 
import matplotlib.pyplot as plt
import scanpy as sc
import sys
import numpy as np
import anndata as ad
import pandas as pd
import seaborn as sns



def basic_clustering(count_matrix_src, cell_info_src, position, dst_dir):
    
    #Get string of position number
    #------------------------------------------------------------
    pos = 'MMStack_Pos13'.split('Pos')[1]
    #------------------------------------------------------------
    
    #Read in count matrix
    #------------------------------------------------------------
    Counts_allPos = pd.read_csv(count_matrix_src, index_col=0).reset_index(drop=True)
    #------------------------------------------------------------


    #Drop fake genes
    #------------------------------------------------------------
    Counts_allPos = Counts_allPos.drop(Counts_allPos[Counts_allPos['gene'].str.contains('fake.')].index).reset_index(drop=True)
    #------------------------------------------------------------


    #Add Pos string to cell name
    #------------------------------------------------------------
    Counts_allPos.columns = [str(col)+'_P'+str(pos) if col != 'gene' else col for col in Counts_allPos.columns]
    #------------------------------------------------------------


    #Read in cell info matrix
    #------------------------------------------------------------
    loc_allPos = pd.read_csv(cell_info_src, index_col=0).reset_index(drop=True)
    loc_allPos['Pos'] = 'P' + str(pos)
    loc_allPos['uniqueCellID'] = 'cell_'+loc_allPos['cellID'].astype(str) + '.0_' + loc_allPos['Pos']
    #------------------------------------------------------------


    #Remove cells that are not in the column names of the Counts dataframe
    #------------------------------------------------------------
    print('cell number before drop', loc_allPos.shape)

    idx = list(set(loc_allPos['uniqueCellID']) - set(Counts_allPos.columns))
    loc_allPos = loc_allPos.loc[~loc_allPos['uniqueCellID'].isin(idx),]

    print('cell number after drop', loc_allPos.shape)
    #------------------------------------------------------------


    #Plot Normalized Counts
    #------------------------------------------------------------
    #create a numpy array of cells x genes
    X = Counts_allPos.iloc[:,1:].to_numpy().transpose()

    #reomve cells with low gene expression
    X = X[np.sum(X, axis=1)>5,]

    #normalize the counts in each cell by to total counts in that cell * 1e3 (normalizing by 1e6 is equivilant ot CMP in RNAseq)
    X_n = 1e3*(X.transpose()/np.tile(np.sum(X,axis=1),(281,1)))
    X_n = X_n.transpose()

    #calculate Z score for each gene over all cells
    X_z = stats.stats.zscore(X_n, axis=1)

    #plot the histograms of the normalized counts
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].hist(X_n.flat,bins=100,range=(min(X_n.flat),max(X_n.flat)))
    axs[0].title.set_text('Normalized By Cell')
    axs[1].hist(X_z.flat,bins=100,range=(min(X_z.flat),max(X_z.flat)))
    axs[1].title.set_text('Z Score Over Cells')
    fig.savefig(os.path.join(dst_dir, 'Normalized_Genes.png'))
    print("Saved Normalized Genes Plots")
    #------------------------------------------------------------


    #Values to set AnnData Object
    #------------------------------------------------------------
    cell_names = pd.DataFrame(index = Counts_allPos.columns.values[1:])
    gene_names = pd.DataFrame(index=Counts_allPos['gene'])
    counts = Counts_allPos.iloc[:,1:].to_numpy().transpose()
    #------------------------------------------------------------

    #Setting AnnData Object
    #------------------------------------------------------------
    adata = ad.AnnData(counts, var = gene_names, obs = cell_names)
    adata.obsm['spatial'] = loc_allPos[['x','y']].to_numpy()
    adata.obs['area']    = loc_allPos['area'].to_numpy()
    adata.obs['position'] = pd.Categorical(loc_allPos['Pos'])
    adata.obs['total counts'] = np.sum(adata.X, axis=1)
    #------------------------------------------------------------

    #Set Directory to save figures
    #------------------------------------------------------------
    sc.settings.figdir = dst_dir
    #------------------------------------------------------------

    #PLot Highly expressed Genes
    #------------------------------------------------------------
    sc.pl.highest_expr_genes(adata, n_top = 20, save='.png')
    plt.savefig(os.path.join(dst_dir, 'high_expr_genes.png'))
    print("Saved Expressed Genes Plot")
    #------------------------------------------------------------

    #Plot and Save Variance Ratio
    #------------------------------------------------------------
    sc.pp.pca(adata)
    sc.pl.pca_variance_ratio(adata, n_pcs = 50, save = '.png')
    print("Saved Variance Ratio Plot")
    #------------------------------------------------------------

    #Show and Plot clusters
    #------------------------------------------------------------
    sc.pp.neighbors(adata)
    sc.tl.umap(adata)
    sc.tl.leiden(adata, key_added="clusters")#,resolution=0.5)
    sc.pl.umap(adata[adata.obs['position'].isin(['P13'])], color=['clusters'],size=50, save='_of_clusters.png') 
    print("Saved UMAP Plots")
    #------------------------------------------------------------
    
import sys

if sys.argv[1] == 'debug_initial_clustering':
    analysis_dir = '/groups/CaiLab/analyses/michalp/michal_1/michal_decoding_top_10000_mat_dapi_all_pos_correct_barcodes/'
    position = 'MMStack_Pos13'
    count_matrix_src = os.path.join(analysis_dir, position, 'Segmentation/Channel_1/count_matrix.csv')
    cell_info_src = os.path.join(analysis_dir, position, 'Segmentation/Channel_1/cell_info.csv')
    dst_dir = 'foo/clustering'
    os.makedirs(dst_dir, exist_ok=True)
    
    basic_clustering(count_matrix_src, cell_info_src, position, dst_dir)