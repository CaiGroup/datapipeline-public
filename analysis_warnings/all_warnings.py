import sys
import os
sys.path.insert(1, os.getcwd())
from analysis_warnings.align_errors_across_pos_s.check_all_align_errors import write_bad_alignment_errors
from analysis_warnings.false_pos_rate_across_positions.write_false_positive_rates_to_file import write_bad_false_pos_s_to_file
from analysis_warnings.see_if_hybs_have_disproportionate_locs.see_outlier_number_of_locs import write_disproporionate_number_of_dots_to_file_for_all_pos

def get_all_warnings(warning_src, analysis_dir):
    
    write_bad_alignment_errors(warning_src, analysis_dir)
    write_disproporionate_number_of_dots_to_file_for_all_pos(warning_src, analysis_dir)
    write_bad_false_pos_s_to_file(warning_src, analysis_dir)
    
if sys.argv[1] == 'debug_all_warnings':
    warning_src = 'foo.txt'
    analysis_dir = '/groups/CaiLab/analyses/michalp/michal_2/michal_2_decoding_test_ch3/'
    get_all_warnings(warning_src, analysis_dir)