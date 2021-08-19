import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import sys

def get_normalized_false_pos_from_file(false_pos_src):
    
    #Read False pos file
    #------------------------------------------------
    f = open(false_pos_src, "r")
    false_pos_contents = f.read()
    #------------------------------------------------
    
    #Get Norm False Positive Rate from file
    #------------------------------------------------
    norm_false_pos = float(false_pos_contents.split('Normalized False Positive Rate in Cells: ')[1].split('\n')[0])
    #------------------------------------------------
    
    return norm_false_pos
    
def get_all_false_pos_files(analysis_dir):
    
    #Get all False Positive Files
    #------------------------------------------------
    glob_me_for_false_pos_files_indiv = os.path.join(analysis_dir, 'MMStack_Pos*', 'False_Positive_Rate_Analysis','Channel*', 'false_positives_after_segmentation.txt')
    glob_me_for_false_pos_files_across = os.path.join(analysis_dir, 'MMStack_Pos*', 'False_Positive_Rate_Analysis', 'false_positives_after_segmentation.txt')
    
    false_pos_files_indiv = glob.glob(glob_me_for_false_pos_files_indiv)
    false_pos_files_across = glob.glob(glob_me_for_false_pos_files_across)
    
    false_pos_files = false_pos_files_indiv + false_pos_files_across
    #------------------------------------------------
    
    return false_pos_files
    
def get_false_pos_dict(false_pos_files):
    
    #Isolate Normalized False Positive Rates
    #------------------------------------------------
    false_pos_dict = {}
    for false_pos_file in false_pos_files:
        
        #Get Norm False Positive
        #------------------------------------------------
        norm_false_pos = get_normalized_false_pos_from_file(false_pos_file)
        #------------------------------------------------
        
        #Get Key for norm false positive
        #------------------------------------------------
        if 'Channel' in false_pos_file:
            pos = false_pos_file.split(os.sep)[7]
            channel = false_pos_file.split(os.sep)[9]
            
            key = pos + ' ' + channel
        else:
            pos = false_pos_file.split(os.sep)[7]
            key = pos
        #------------------------------------------------
        
        #Set to key
        #------------------------------------------------
        false_pos_dict[key] = round(norm_false_pos, 3)
        #------------------------------------------------
    
    #------------------------------------------------
    
    return false_pos_dict
    
def plot_false_pos_dict(false_pos_dict, dst):
    
    #Make Plot
    #------------------------------------------------
    plt.figure()
    plt.title('Normalized False Positive Rate For Every Position and Channel')
    plt.ylabel('Normalized False Positive Rate')
    plt.axhline(y=.5, color='red')
    plt.text(0, .52, 'Should Not be above Red Line')
    y_nums = np.round(np.arange(0,1,.1),1)
    plt.yticks(y_nums, y_nums)
    plt.grid(axis="y")
    
    plt.bar(range(len(false_pos_dict)), list(false_pos_dict.values()), align='center')
    plt.xticks(range(len(false_pos_dict)), list(false_pos_dict.keys()), rotation='vertical', fontsize=10)
    plt.tight_layout()
    plt.savefig(dst)
    #------------------------------------------------ 
    
def get_false_pos_analytics(false_pos_dict, false_pos_analytics_dst):
    
    #Get list of norm false positives
    #---------------------------------------------------------
    norm_false_pos_s = list(false_pos_dict.values())
    #---------------------------------------------------------
    
    #Get Analytics
    #---------------------------------------------------------
    mean_norm_false_pos = np.mean(norm_false_pos_s)
    var_norm_false_pos = np.var(norm_false_pos_s)
    percentile_25_norm_false_pos = np.percentile(norm_false_pos_s, 25)
    percentile_75_norm_false_pos = np.percentile(norm_false_pos_s, 75)
    #---------------------------------------------------------
    
    #Write to file 
    #---------------------------------------------------------
    file1 = open(false_pos_analytics_dst,"w")
    file1.write("Mean Normalized False Positive Rate: " + str(round(mean_norm_false_pos*100,2)) + '% \n')
    file1.write("Variance of Normalized False Positive Rate: " + str(round(var_norm_false_pos*100, 2)) + '\n')
    file1.write("25th Percentile of Normalized False Positive Rate: " + str(round(percentile_25_norm_false_pos*100, 2)) + '% \n')
    file1.write("75th Percentile of Normalized False Positive Rate: " + str(round(percentile_75_norm_false_pos*100, 2)) + '% \n')
    file1.close() 
    #---------------------------------------------------------
    
    
def show_norm_false_pos_metrics(analysis_dir, dst_dir):
    
    os.makedirs(dst_dir, exist_ok=True)
    
    #Get False Positive FIles from analysis dir
    #------------------------------------------------
    false_pos_files = get_all_false_pos_files(analysis_dir)
    #------------------------------------------------
    
    #Get False Positive Dictionary from files
    #------------------------------------------------
    false_pos_dict = get_false_pos_dict(false_pos_files)
    #------------------------------------------------
    
    #Get False Positive Plot from dictionary
    #------------------------------------------------
    false_pos_plot_dst = os.path.join(dst_dir, 'All_Normalized_False_Positives.png')
    plot_false_pos_dict(false_pos_dict, false_pos_plot_dst)
    #------------------------------------------------
    
    #Get False Positive Mean and Variance
    #------------------------------------------------
    false_pos_mean_and_var_dst = os.path.join(dst_dir, 'False_Positive_Rate_Analytics.txt')
    get_false_pos_analytics(false_pos_dict, false_pos_mean_and_var_dst )
    print(f'{false_pos_mean_and_var_dst=}')
    #------------------------------------------------
    

if __name__ == '__main__':

    if sys.argv[1] == 'debug_false_pos_all_pos':
        analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot/'
        dst = 'foo/jina_pseudo_4_strict_0'

        show_norm_false_pos_metrics(analysis_dir, dst)

    if sys.argv[1] == 'debug_false_pos_all_pos_strict_1':
        analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot_strict_1/'
        dst = 'foo/jina_pseudo_4_strict_1'

        show_norm_false_pos_metrics(analysis_dir, dst)

    if sys.argv[1] == 'debug_false_pos_all_pos_strict_2':
        analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot_strict_2/'
        dst = 'foo/jina_pseudo_4_strict_2'

        show_norm_false_pos_metrics(analysis_dir, dst)
    
    
    
    
    
    
    