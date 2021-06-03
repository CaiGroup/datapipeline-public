import pandas as pd 
import matplotlib.pyplot as plt

def get_z_slices_check_img(self, df,dst_dir):
    
    #Get the number of dots in each z
    #------------------------------------------------------
    z_s = np.array(np.round(df.z))+1
    #------------------------------------------------------
    
    #Plot and save the figure
    #------------------------------------------------------
    plt.figure()
    plt.title("Number of Dots Across Z's", fontsize=20)
    plt.xlabel("Z Slice")
    plt.ylabel("Number of Dots")
    plt.xticks(list(set(z_s)))
    plt.hist(z_s)
    plt.savefig(os.path.join(dst_dir, 'Dots_Across_Z_Slices.png'))
    #------------------------------------------------------

def get_heatmap_of_xy(self, df, dst_dir):
    
    #Get size and tiles across
    #------------------------------------------------------
    size = int(np.round(df[['x','y']].values.max()))
    tiles_across = 16
    print(f'{size=}')
    #------------------------------------------------------
    
    #Get the heatmap sections
    #------------------------------------------------------
    heatmap_sections = []
    step_size = int(np.round(size/tiles_across))
    for x in range(0,size,step_size):
        heatmap_slide = []
        for y in range(0,size,step_size):
            df_square = df[(df.x >= x) & (df.x <=(x+512)) & \
                           (df.y >=y) & (df.y <=(y+512))]

            heatmap_slide.append(df_square.shape[0])

        heatmap_sections.append(heatmap_slide)
    #------------------------------------------------------
    
    #Run some quick reformatting
    #------------------------------------------------------
    heatmap_sections.reverse()
    heatmap_sections = np.array(heatmap_sections)
    heatmap_sections = np.rot90(heatmap_sections,2).T
    #------------------------------------------------------

    #Plot the heatmap
    #------------------------------------------------------
    colormap = sns.color_palette("Greens")
    plt.figure()
    plt.title('Map of Locations Across X and Y', fontsize=15)
    map_xy = sns.heatmap(heatmap_sections, cmap=colormap)
    map_xy.set_xticklabels(list(range(0,size,step_size)), fontsize = 5)
    map_xy.set_yticklabels(list(range(0,size,step_size)), fontsize = 5)
    
    plt.savefig(os.path.join(dst_dir, 'Map_of_XY_Locations.png'))
    #------------------------------------------------------
    
def get_location_checks(self, locations_csv_src):
    
    #Make dst dir
    #------------------------------------------------------
    dst_dir = os.path.join(os.path.dirname(locations_csv_src), 'Location_Checks')
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    #------------------------------------------------------
    
    #Read dataframe and get checks
    #------------------------------------------------------
    df = pd.read_csv(locations_csv_src)
    self.get_z_slices_check_img(df,dst_dir)
    self.get_heatmap_of_xy(df, dst_dir)
    #------------------------------------------------------
    
    
def get_n_dots_for_each_channel_plot(locs_src, dst):
    #Read in locations
    #----------------------------------------------------------
    df_locs = pd.read_csv(locs_src)
    #----------------------------------------------------------
    
    #Get the number of dots for each hyb and ch
    #----------------------------------------------------------
    df_n_dots = pd.DataFrame(columns = ['hyb', 'ch', 'n_dots'])
    for hyb in df_locs.hyb.unique():
        for ch in df_locs.ch.unique():
            df_hyb_ch = df_locs[(df_locs.hyb == hyb) & (df_locs.ch == ch)]
            df_n_dots = df_n_dots.append({'hyb':hyb, 'ch':ch, 'n_dots':df_hyb_ch.shape[0]}, ignore_index=True)
    #----------------------------------------------------------
    
    #Declare the subplots
    #----------------------------------------------------------
    fig, axs = plt.subplots(len(df_n_dots.ch.unique()))
    fig.suptitle('Number of Dots Across Channels and Hybs', fontsize=15)
    fig.tight_layout(pad=2.0)
    plt.xlabel('HybCycles', fontsize=12)
    fig.text(0, 0.5, 'Number of Dots', va='center', rotation='vertical', 
            fontsize=12)
    #----------------------------------------------------------
    
    
    #Make the barcharts
    #----------------------------------------------------------
    if len(df_n_dots.ch.unique()) > 1:
        for ch_i in range(len(df_n_dots.ch.unique())):
            print(f'{ch_i=}')
            df_n_dots_ch = df_n_dots[df_n_dots.ch == df_n_dots.ch.unique()[ch_i]]
            axs[ch_i].bar(range(len(df_n_dots_ch.n_dots)), df_n_dots_ch.n_dots)
            axs[ch_i].set_title('Channel ' + str(df_n_dots.ch.unique()[ch_i]),
                               fontsize=10)
    elif len(df_n_dots.ch.unique()) == 1:
        ch_i = 0
        print(f'{ch_i=}')
        df_n_dots_ch = df_n_dots[df_n_dots.ch == df_n_dots.ch.unique()[ch_i]]
        axs.bar(range(len(df_n_dots_ch.n_dots)), df_n_dots_ch.n_dots)
        axs.set_title('Channel ' + str(df_n_dots.ch.unique()[ch_i]))
    #----------------------------------------------------------
    
    #Save plot
    #----------------------------------------------------------
    plt.savefig(dst)
    #----------------------------------------------------------
    
import sys

if sys.argv[1] == 'debug_n_dots_check':
    locs_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/test/MMStack_Pos8/Dot_Locations/locations.csv'
    dst = 'foo.png'
    get_n_dots_for_each_channel_plot(locs_src, dst)








