import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    dist_2 = np.sum(np.absolute((nodes - node)**3), axis=1)
    #print(f'{dist_2=}')
    return np.argmin(dist_2), np.min(dist_2)

def colocalize_lists(dots1, dots2):
    colocs = []
    for dot in dots1:
        colocs.append(list(closest_node(dot, dots2)))
    
    return colocs

def remove_non_coloced_for_final_dots(df_final, colocs):
    final_indices_drop = []
    for i in range(len(colocs)):
        if colocs[i][1] > 100:
            final_indices_drop.append(i)
            
    df_final_coloced = df_final.drop(final_indices_drop)
    return df_final_coloced

def remove_non_coloced_for_initial_dots(df_init, colocs):
    init_indices_used = []
    for i in range(len(colocs)):
        if colocs[i][1] < 100:
            init_indices_used.append(colocs[i][0])

    init_indices_used  = list(set(init_indices_used))
    print(f'{init_indices_used=}')
    init_indices_drop = np.setdiff1d(list(df_init.index), init_indices_used)
    print(f'{init_indices_drop=}')

    df_init_coloced = df_init.drop(init_indices_drop)
    return df_init_coloced
    
def get_plotted_colocs(df_final, df_init, dst_dir):
    
    plt.figure(figsize=(20,20))
    plt.scatter(df_final.x, df_final.y, label ='Final Fiducials', s=1000)
    plt.scatter(df_init.x, df_init.y, label ='Initial Fiducials', s=200)
    plt.legend(fontsize=20, facecolor='y')
    plt.savefig(os.path.join(dst_dir, 'Check_Colocalization.png'))
    
def get_plotted_colocs_multiple_z_s(df_f, df_i, dst_dir):
    fig, axs = plt.subplots(len(df_i.z.unique()))
    fig.set_figheight(30)
    fig.set_figwidth(15)
    for i in range(len(df_i.z.unique())):
        df_f_z = df_f[df_f.z == df_f.z.unique()[i]]
        axs[i].scatter(df_f_z.x, df_f_z.y, s= 400,label ='Final Fiducials')

        df_i_z = df_i[df_i.z == df_i.z.unique()[i]]
        axs[i].scatter(df_i_z.x, df_i_z.y, s =90,label ='Initial Fiducials')

    check_coloc_dst = os.path.join(dst_dir, 'Check_Multiple_Z_Colocalization.png')
    plt.savefig(check_coloc_dst)
    
def get_colocs(final_src, init_src):
    print(f'{final_src=}')
    print(f'{init_src=}')
    df_init = pd.read_csv(init_src)
    df_final = pd.read_csv(final_src)
    init_dots = np.array(df_init[['x','y','z']])
    final_dots = np.array(df_final[['x','y','z']])
    
    colocs = colocalize_lists(final_dots, init_dots)
    print(f'{colocs=}')
    
    df_final_coloced = remove_non_coloced_for_final_dots(df_final, colocs)
    df_init_coloced = remove_non_coloced_for_initial_dots(df_init, colocs)
    
    df_final_coloced.to_csv(final_src, index=False)
    df_init_coloced.to_csv(init_src, index=False)
    get_plotted_colocs_multiple_z_s(df_final_coloced, df_init_coloced, os.path.dirname(final_src))
    get_plotted_colocs(df_final_coloced, df_init_coloced, os.path.dirname(final_src))
    print('Shape of Colocalized Final Fiducials:', str(df_final_coloced.shape))
    print('Shape of Colocalized Initial Fiducials:', str(df_init_coloced.shape))
    return df_final_coloced, df_init_coloced

if __name__ == '__main__':

    if sys.argv[1] == 'debug_coloc':
        final_src = 'foo/test_fid_alignment2/final_fids/locs.csv'
        init_src = 'foo/test_fid_alignment2/initial_fids/locs.csv'

        get_colocs(final_src, init_src)
    
    
    
    