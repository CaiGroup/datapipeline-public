import numpy as np
import pandas as pd
import sys

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
        if colocs[i][1] > 3:
            final_indices_drop.append(i)
            
    df_final_coloced = df_final.drop(final_indices_drop)
    return df_final_coloced

def remove_non_coloced_for_initial_dots(df_init, colocs):
    init_indices_used = []
    for i in range(len(colocs)):
        if colocs[i][1] < 3:
            init_indices_used.append(colocs[i][0])

    init_indices_used  = list(set(init_indices_used))
    print(f'{init_indices_used=}')
    init_indices_drop = np.setdiff1d(list(df_init.index), init_indices_used)
    print(f'{init_indices_drop=}')

    df_init_coloced = df_init.drop(init_indices_drop)
    return df_init_coloced
    
def get_colocs(df_final, df_init):
    init_dots = np.array(df_init[['x','y','z']])
    final_dots = np.array(df_final[['x','y','z']])
    
    colocs = colocalize_lists(final_dots, init_dots)
    print(f'{colocs=}')
    
    df_final_coloced = remove_non_coloced_for_final_dots(df_final, colocs)
    df_init_coloced = remove_non_coloced_for_initial_dots(df_init, colocs)
    
    return df_final_coloced, df_init_coloced

if sys.argv[1] == 'debug_coloc':
    final_src = 'foo/test_fid_alignment/final_fids/locs.csv'
    init_src = 'foo/test_fid_alignment/initial_fids/locs.csv'
    df_init = pd.read_csv(init_src)
    df_final = pd.read_csv(final_src)
    
    get_colocs(df_final, df_init)