import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot_hyb_locs_on_fids(locs_src, final_fids_src, initial_fids_src, dst):

    #Read locs into Dataframe
    #----------------------------------------------------
    df_locs = pd.read_csv(locs_src)
    df_final_fids = pd.read_csv(final_fids_src)
    df_init_fids = pd.read_csv(initial_fids_src)
    #----------------------------------------------------
    
    #Plot hyb locs on fids
    #----------------------------------------------------
    plt.figure(figsize=(20,20))
    plt.scatter(df_final_fids.x, df_final_fids.y, s= 200)
    plt.scatter(df_init_fids.x, df_init_fids.y, s=200)
    plt.scatter(df_locs.x.head(100000), df_locs.y.head(100000))
    #----------------------------------------------------
    
    #Save plot to dst
    #----------------------------------------------------
    plt.savefig(dst)
    #----------------------------------------------------

if __name__ == '__main__':

    if sys.argv[1] ==  'debug_hyb_locs_on_fids':
        plot_hyb_locs_on_fids(locs_src = '/groups/CaiLab/analyses/nrezaee/linus_data/linus_fid/MMStack_Pos0/Dot_Locations/locations.csv',
                             final_fids_src = '/groups/CaiLab/analyses/nrezaee/linus_data/linus_fid/MMStack_Pos0/Alignment/final_fids/locs.csv',
                             initial_fids_src = '/groups/CaiLab/analyses/nrezaee/linus_data/linus_fid/MMStack_Pos0/Alignment/initial_fids/locs.csv',
                             dst = 'foo/hyb_locs_on_fids_check.png')
        print('Finished Plotting')