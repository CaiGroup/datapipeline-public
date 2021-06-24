import os 
import glob
import json
import sys

def get_tifs_with_bad_dapi_alignment(analysis_dir):
    
    #Get ali alignment errors jsons files
    #--------------------------------------------
    glob_me_for_align_errors = os.path.join(analysis_dir, 'MMStack_Pos*', 'align_errors.json')
    all_align_errors_jsons = glob.glob(glob_me_for_align_errors)
    #--------------------------------------------
    
    
    #Loop though ailgnmnet errors jsons
    #--------------------------------------------
    bad_alignment_errors = []
    total_number_of_tifs_aligned = 0
    for align_error_json in all_align_errors_jsons:
        
        #Read json file
        #--------------------------------------------
        json_info = open(align_error_json)
        align_errors_dict = json.load(json_info)
        #--------------------------------------------
        
        #Loop through each dict and get bad alignments
        #--------------------------------------------
        for key in align_errors_dict.keys():
            if 'Worsened' in align_errors_dict[key]:
                bad_alignment_errors.append(key.replace('align_error_', ''))
            total_number_of_tifs_aligned +=1
        #--------------------------------------------
        
    return bad_alignment_errors
    
def write_bad_alignment_errors(warnings_src, analysis_dir):
    
    #Get badly aligned tifs
    #--------------------------------------------
    badly_aligned_tifs = get_tifs_with_bad_dapi_alignment(analysis_dir)
    badly_aligned_tifs_to_write = ['    ' + tif + ' \n' for tif in badly_aligned_tifs]
    #--------------------------------------------
    
    #Write to file
    #--------------------------------------------
    warnings_file = open(warnings_src, 'a+')
    warnings_file.write('Dapi Alignment Issues \n')
    if len(badly_aligned_tifs_to_write) > 0:
        warnings_file.writelines(badly_aligned_tifs_to_write)
    else:
        warnings_file.write('    None \n')
        
    warnings_file.close()
    #--------------------------------------------
    

if sys.argv[1] == 'debug_warnings_align_errors':
    analysis_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_mat_dapi_mat_dot/'
    warnings_src = 'foo.txt'
    bad_alignment_errors = write_bad_alignment_errors(warnings_src, analysis_dir)
    print(f'{bad_alignment_errors=}')