import os
import glob
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

def get_bad_false_pos_s(analysis_dir):
    
    #Get all False Positive Files
    #------------------------------------------------
    glob_me_for_false_pos_files_indiv = os.path.join(analysis_dir, 'MMStack_Pos*', 'False_Positive_Rate_Analysis','Channel*', 'false_positives_after_segmentation.txt')
    glob_me_for_false_pos_files_across = os.path.join(analysis_dir, 'MMStack_Pos*', 'False_Positive_Rate_Analysis', 'false_positives_after_segmentation.txt')
    
    false_pos_files_indiv = glob.glob(glob_me_for_false_pos_files_indiv)
    false_pos_files_across = glob.glob(glob_me_for_false_pos_files_across)
    
    false_pos_files = false_pos_files_indiv + false_pos_files_across
    #------------------------------------------------
    
    
    #Get Norm False Positive from files
    #------------------------------------------------
    bad_threshold = .3
    
    bad_norm_false_pos_s = {}
    for false_pos_file in false_pos_files:
        norm_false_pos = get_normalized_false_pos_from_file(false_pos_file)
        if norm_false_pos > bad_threshold:
            bad_norm_false_pos_s[false_pos_file] = norm_false_pos
    #------------------------------------------------
    
    return bad_norm_false_pos_s
    
def get_lines_to_write_from_dict(bad_norm_false_pos_s_dict):
    
    #Get lines to write
    #------------------------------------------------
    false_pos_lines_to_write = []
    for key, value in bad_norm_false_pos_s_dict.items():
        false_pos_lines_to_write.append('        ' + key.split(os.sep)[7].replace('MMStack_', '') + ' ' + key.split(os.sep)[9] + ' ' + str(round(value, 2)) + '\n')
    #------------------------------------------------
    
    return false_pos_lines_to_write 
    
    
def write_bad_false_pos_s_to_file(warnings_src, analysis_dir):
    
    bad_norm_false_pos_s_dict = get_bad_false_pos_s(analysis_dir)
    
    false_pos_lines_to_write = get_lines_to_write_from_dict(bad_norm_false_pos_s_dict)
    
    #Write to File
    #------------------------------------------------
    warnings_file = open(warnings_src, 'a+')
    warnings_file.write('Decoding Issues \n')
    warnings_file.write('    False Positive Rate Issues \n')
    if len(false_pos_lines_to_write) > 0:
        warnings_file.writelines(false_pos_lines_to_write)
    else:
        warnings_file.write('        None \n')
    warnings_file.close()
    #------------------------------------------------
    
    print(f'{warnings_src=}')
    
    
if __name__ == '__main__':

    if sys.argv[1] == 'debug_warnings_false_pos_rate':
        analysis_dir = '/groups/CaiLab/analyses/michalp/michal_2/michal_2_decoding_test_ch3/'
        warnings_dst = 'foo.txt'
        write_bad_false_pos_s_to_file(warnings_dst, analysis_dir)



