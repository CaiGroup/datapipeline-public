import os 
import sys
import glob
import matplotlib.pyplot as plt


def get_percent_used(percent_src):
    
    #Read in percent file
    #-----------------------------------------------------------
    f = open(percent_src, "r")
    percent_data = f.read()
    #-----------------------------------------------------------

    #Get percent used
    #-----------------------------------------------------------
    percent_used = float(percent_data.split('Used ')[1].split('%')[0])
    #-----------------------------------------------------------
    
    return percent_used
    
def get_all_percent_of_dot_srcs(analysis_dir):
    
    #Get all percent of dots srcs
    #-----------------------------------------------------------
    glob_me_for_percent_of_dots = os.path.join(analysis_dir, 'MMStack_Pos*', 'Decoded', 'Channel*', 'percentage_of_dots_used.txt')
    percent_of_dots_srcs = glob.glob(glob_me_for_percent_of_dots)
    print(f'{percent_of_dots_srcs=}')
    #-----------------------------------------------------------
    
    return percent_of_dots_srcs
    
def get_percent_of_dots_dict(percent_of_dots_srcs):
    
    #Get Percent of dots used dict
    #-----------------------------------------------------------
    percent_used_dict = {}
    for percent_of_dots_src in percent_of_dots_srcs:
        
        #Get key
        #-----------------------------------------------------------
        pos = percent_of_dots_src.split(os.sep)[7]
        channel = percent_of_dots_src.split(os.sep)[9]
        key = pos + ' ' + channel
        #-----------------------------------------------------------
        
        #Add to dict
        #-----------------------------------------------------------
        percent_used_dict[key] = get_percent_used(percent_of_dots_src)
        #-----------------------------------------------------------
        
    print(f'{percent_used_dict=}')
    #-----------------------------------------------------------    
    
    return percent_used_dict
    
def get_percent_of_dots_used_plot(percent_used_dict, dst):
    
    #Make Plot
    #------------------------------------------------
    plt.figure()
    plt.title('Percentage of Dots Used For Each Position and Channel')
    plt.ylabel('Percentage of Dots Used')
    plt.grid(axis="y")
    
    plt.bar(range(len(percent_used_dict)), list(percent_used_dict.values()), align='center')
    plt.xticks(range(len(percent_used_dict)), list(percent_used_dict.keys()), rotation='vertical', fontsize=10)
    plt.tight_layout()
    plt.savefig(dst)
    #------------------------------------------------     
    
    
def comb_percentage_of_dots_used_and_get_plot(analysis_dir, dst):
    
    os.makedirs(os.path.dirname(dst), exist_ok = True)
    
    #Get all percentage of dot srcs
    #------------------------------------------------     
    percent_of_dots_srcs = get_all_percent_of_dot_srcs(analysis_dir)
    #------------------------------------------------     
    
    #Get percent of dots used dict
    #------------------------------------------------     
    percent_used_dict = get_percent_of_dots_dict(percent_of_dots_srcs)
    #------------------------------------------------     
    
    #Get plot of percent of dots used
    #------------------------------------------------     
    get_percent_of_dots_used_plot(percent_used_dict, dst)
    #------------------------------------------------     

if sys.argv[1] == 'debug_get_percent_of_dots':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot'
    dst = 'foo.png'

    comb_percentage_of_dots_used_and_get_plot(analysis_dir, dst)



