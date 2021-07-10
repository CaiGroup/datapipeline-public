import filecmp
import os
from scipy.io import loadmat

main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']


def offsets_test(experiment_name, analysis_name, result):
    
    offset_path = os.path.join(main_dir, 'analyses/nrezaee', experiment_name, analysis_name, 'MMStack_Pos0/offsets.json')
    if os.path.isfile(offset_path):
        result+="|| No align test                 || Passed! \n"
        
    else: 
        result+="|| No align test                 || Failed! \n"
        
    return result    
    
def dot_detection_test(experiment_name, analysis_name, locs_path, result):
    
    dot_detection_path = os.path.join(main_dir, 'analyses/nrezaee', experiment_name, analysis_name,'MMStack_Pos0', locs_path)
    if os.path.isfile(dot_detection_path):
        result+="|| Dot Detection test            || Passed!\n"
    else:
        result+="|| Dot Detection test            || Failed!\n"
        
    return result    
    
def decoding_test(decoded_dir, result):

    #Declare where files should be
    #--------------------------------
    where_finalPosList_mat_should_be = os.path.join(decoded_dir,'finalPosList.mat')
    where_PosList_mat_should_be = os.path.join(decoded_dir, 'PosList.mat')
    where_seeds_mat_should_be = os.path.join(decoded_dir,'seeds.mat')
    #--------------------------------
    
    #Check to see if files exist
    #--------------------------------
    if os.path.isfile(where_finalPosList_mat_should_be) and  \
       os.path.isfile(where_PosList_mat_should_be) and  \
       os.path.isfile(where_seeds_mat_should_be):
    
        result+="|| Decoding test                 || Passed!\n"
    else:
        result+="|| Decoding test                 || Failed!\n"
    #--------------------------------
    
    return result
    
def alignment_errors_test(alignment_file, result):
    

    if os.path.exists(alignment_file):
                  
        result+="|| Alignment errors test         || Passed!\n"
    else:
        result+="|| Alignment errors test         || Failed!\n"
    #--------------------------------------------------------------------------------------
    
    return result

def locations_shape_test(locations_src, result):
    
    locations = loadmat(locations_src)
    
    if locations["locations"].shape == (12,2):
        result+="|| Locations Shape test          || Passed!\n"
    else:
        result+="|| Locations Shape test          || Failed!\n"
    #--------------------------------------------------------------------------------------

    return result
    
def segmentation_test(seg_dir, result):

    #Declare where files should be
    #--------------------------------
    label_src = os.path.join(seg_dir,'3d_labeled_img.tiff')
    cell_info_src = os.path.join(seg_dir, 'cell_info.csv')
    count_matrix_src = os.path.join(seg_dir,'count_matrix.csv')
    assigned_src = os.path.join(seg_dir,'gene_locations_assigned_to_cell.csv')
    #--------------------------------
    
    #Check to see if files exist
    #--------------------------------
    if os.path.isfile(label_src) and  \
       os.path.isfile(cell_info_src) and  \
       os.path.isfile(count_matrix_src) and \
       os.path.isfile(assigned_src):
    
        result+="|| Segmentation test                 || Passed!\n"
    else:
        result+="|| Segmentation test                 || Failed!\n"
    #--------------------------------
    
    return result
    
#====================================================================================================================================

def check_3d_across_test():
    experiment_name  = 'test1'
    result = """3d Across Results\n"""

    result = offsets_test(experiment_name, '3d_across', result)
    
    result = dot_detection_test('test1', '3d_across', 'Dot_Locations/locations.mat', result)
        
    decoded_dir = os.path.join(main_dir, 'analyses/nrezaee', experiment_name, '3d_across/MMStack_Pos0/Decoded/')
    result = decoding_test(decoded_dir, result)
    
    align_errors_src = os.path.join(main_dir,'analyses/nrezaee/', experiment_name, '3d_across/MMStack_Pos0/errors_for_alignment.json')
    result = alignment_errors_test(align_errors_src, result)
    
    where_locations_mat_should_be = main_dir+ '/analyses/nrezaee/'+experiment_name+'/3d_across/MMStack_Pos0/Dot_Locations/locations.mat'
    result = locations_shape_test(where_locations_mat_should_be, result)
    
    print(result)

    
def check_3d_indiv_test():
    experiment_name = 'test1-indiv'
    
    result = """3d Indiv Results\n"""

    result = offsets_test(experiment_name, '3d_indiv', result)
    
    
    result = dot_detection_test('test1-indiv', '3d_indiv', 'Dot_Locations/locations.mat', result)
    
    decoded_dir = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '3d_indiv/MMStack_Pos0/Decoded/Channel_1/')
    result = decoding_test(decoded_dir, result)

    
    #Checks if Alignmnet Errors Test
    #--------------------------------------------------------------------------------------
    align_errors_src = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '3d_indiv/MMStack_Pos0/errors_for_alignment.json')
    result = alignment_errors_test(align_errors_src, result)
    
    #Checks if locations has correct shape
    #--------------------------------------------------------------------------------------
    
    where_locations_mat_should_be = main_dir+ '/analyses/nrezaee/'+experiment_name+'/3d_indiv/MMStack_Pos0/Dot_Locations/locations.mat'
    result = locations_shape_test(where_locations_mat_should_be, result)
    
    print(result)
    
def check_2d_across_test():
    
    experiment_name = 'test1'
    result = """2d Across\n"""

    result = offsets_test(experiment_name, '2d_across', result)
    
    
    result = dot_detection_test('test1', '2d_across', 'Dot_Locations/locations_z_0.mat', result)
    
    decoded_dir = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '2d_across/MMStack_Pos0/Decoded/Z_Slice_0')
    result = decoding_test(decoded_dir, result)

    
    #Checks if Alignmnet Errors Test
    #--------------------------------------------------------------------------------------
    align_errors_src = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '3d_indiv/MMStack_Pos0/errors_for_alignment.json')
    result = alignment_errors_test(align_errors_src, result)
    
    #Checks if locations has correct shape
    #--------------------------------------------------------------------------------------
    
    where_locations_mat_should_be = main_dir+ '/analyses/nrezaee/'+experiment_name+'/3d_indiv/MMStack_Pos0/Dot_Locations/locations.mat'
    result = locations_shape_test(where_locations_mat_should_be, result)
    
    print(result)
    
def check_2d_indiv_test():
    
    experiment_name = 'test1-indiv'
    result = """2d Across\n"""

    result = offsets_test(experiment_name, '2d_across', result)
    
    
    result = dot_detection_test('test1', '2d_across', 'Dot_Locations/locations_z_0.mat', result)
    
    decoded_dir = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '2d_across/MMStack_Pos0/Decoded/Z_Slice_0')
    result = decoding_test(decoded_dir, result)

    
    #Checks if Alignmnet Errors Test
    #--------------------------------------------------------------------------------------
    align_errors_src = os.path.join(main_dir, 'analyses/nrezaee/', experiment_name, '3d_indiv/MMStack_Pos0/errors_for_alignment.json')
    result = alignment_errors_test(align_errors_src, result)
    
    #Checks if locations has correct shape
    #--------------------------------------------------------------------------------------
    
    where_locations_mat_should_be = main_dir+ '/analyses/nrezaee/'+experiment_name+'/3d_indiv/MMStack_Pos0/Dot_Locations/locations.mat'
    result = locations_shape_test(where_locations_mat_should_be, result)
    
    print(result) 
    
    
    
    
