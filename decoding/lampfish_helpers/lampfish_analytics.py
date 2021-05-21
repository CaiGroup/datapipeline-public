import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import sys

def get_ratio_visualization(locs_src, dst):
    
    df_locs = pd.read_csv(locs_src)
    #df_locs['ratio'] = df_locs['sum_3x3_int_ch1']/(df_locs['sum_3x3_int_ch2'] + df_locs['sum_3x3_int_ch1'])
    df_locs = df_locs[df_locs['ratio'] != np.inf]
    #color = sns.color_palette()[2:10]
    plt.figure()
    sns.histplot(data=df_locs, x="ratio", hue="hyb",bins=300).set_title('Ratio')
    plt.savefig(dst)
    
if sys.argv[1] == 'debug_ratio_vis':
    get_ratio_visualization(locs_src = 'foo/lampfish_decoding.csv',
                            dst= 'foo/ratio_visual.png')