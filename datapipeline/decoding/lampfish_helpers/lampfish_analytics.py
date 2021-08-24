import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def get_ratio_visualization(locs_src, dst):
    """
    Get visuals of ratio from locs_src
    Inputs:
        locs_src : locations of lampfish results
        dst : where the destination of the plot will be
    Output:
        Save png file to dst
    """
    # Read in locations src and remove cases on the edges which cause inf
    # --------------------------------------------------
    df_locs = pd.read_csv(locs_src)
    df_locs = df_locs[df_locs['ratio'] != np.inf]
    # --------------------------------------------------

    # Plot figure
    # --------------------------------------------------
    plt.figure()
    sns.histplot(data=df_locs, x="ratio", hue="hyb", bins=300).set_title('Ratio')
    plt.savefig(dst)
    # --------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_ratio_vis':
        get_ratio_visualization(locs_src='foo/lampfish_decoding.csv',
                                dst='foo/ratio_visual.png')
