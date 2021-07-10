import glob
import os
import matplotlib.pyplot as plt
import imageio as io
import tifffile as tf
import numpy as np
import sys


def get_analysis_pos_dir(tiff_src, analysis_name):
    
    #Split Tiff src
    #------------------------------------------------
    all_analyses_dir = '/groups/CaiLab/analyses'
    
    splitted_tiff_src = tiff_src.split(os.sep)
    personal = splitted_tiff_src[4]
    exp_name = splitted_tiff_src[6]
    hyb = splitted_tiff_src[-2]
    pos = tiff_src.split(os.sep)[-1].split('.ome')[0]
    #------------------------------------------------
    
    #Combine to analysis dir
    #------------------------------------------------
    analysis_pos_dir = os.path.join(all_analyses_dir, personal, exp_name, analysis_name, pos)
    #------------------------------------------------
    
    return analysis_pos_dir, hyb 
    
    
def see_what_dirs_exist(dirs_with_checks):
    
    #See what directories exist
    #-----------------------------------------------------
    for dir_with_check in dirs_with_checks:
        if os.path.isdir(dir_with_check):
            pass
        else:
            #print(f'{dir_with_check=}')
            dirs_with_checks.remove(dir_with_check)
    
    print(f'{dirs_with_checks=}')
    #-----------------------------------------------------
    
    return dirs_with_checks


def side_by_side_preprocess_checks(tiff_src, analysis_name):

    #Get Analysis pos dir
    #-----------------------------------------------------
    analysis_pos_dir, hyb = get_analysis_pos_dir(tiff_src, analysis_name)
    #-----------------------------------------------------
    
    #List possible directories
    #-----------------------------------------------------
    back_sub_check_dir = os.path.join(analysis_pos_dir, 'Back_Sub_Check')
    back_blob_removal_check = os.path.join(analysis_pos_dir, 'Back_Blob_Removal_Check')
    tophat_check = os.path.join(analysis_pos_dir, 'Tophat_Check')
    blur_check = os.path.join(analysis_pos_dir, 'Blur_Check')
    rolling_ball_check = os.path.join(analysis_pos_dir, 'Rolling_Ball_Check')
    raw_image = os.path.join(analysis_pos_dir, 'Raw_Image')
    
    dirs_with_checks = [raw_image, back_sub_check_dir, blur_check, back_blob_removal_check, tophat_check, rolling_ball_check]
    #-----------------------------------------------------
    
    dirs_with_checks = see_what_dirs_exist(dirs_with_checks)
    
    
    if len(dirs_with_checks) > 0:
        
        #Make Dot Detection Checks Dir
        #-----------------------------------------------------
        pre_dot_detection_checks_dir = os.path.join(analysis_pos_dir, 'Pre_Dot_Detection_Checks')
        os.makedirs(pre_dot_detection_checks_dir, exist_ok = True)
        #-----------------------------------------------------
        
        #Declare Png file name
        #-----------------------------------------------------
        glob_me_for_png_file_names = os.path.join(dirs_with_checks[0], hyb + '*')
        png_file_full_paths = glob.glob(glob_me_for_png_file_names)
        png_file_names = [os.path.basename(png_file_path) for png_file_path in png_file_full_paths]
        #-----------------------------------------------------
    
        #Declare Matplolib figure
        #-----------------------------------------------------
        fig, axs = plt.subplots(1, len(dirs_with_checks), figsize=(20,20))
        #-----------------------------------------------------
        
        #Loop through each HybCycle and Channel
        #-----------------------------------------------------
        for png_file_name in png_file_names:
            
            print(f'{png_file_name=}')

            #Loop through each check
            #-----------------------------------------------------
            for i in range(len(dirs_with_checks)):
                print(f'{i=}')
                
                #Get img path
                #--------------------------------------------------
                img_src = os.path.join(dirs_with_checks[i], png_file_name)
                print(f'{img_src=}')
                #--------------------------------------------------
                
                #Plot if path exists (sometimes one path may not exist because of the dot detection notebook
                #--------------------------------------------------
                if os.path.exists(img_src):
                    img = io.imread(img_src)
                
                    axs[i].imshow(img, cmap='gray')
                    axs[i].title.set_text(os.path.basename(dirs_with_checks[i]))
                else:
                    pass
                #--------------------------------------------------
                
                
            #Save plot
            #-----------------------------------------------------
            dst_of_check = os.path.join(pre_dot_detection_checks_dir, png_file_name)
            print(f'{dst_of_check=}')
            fig.savefig(dst_of_check)
            #-----------------------------------------------------
            
            
if sys.argv[1] == 'debug_side_by_side_check':
    
    tiff_src = '/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_4_corrected/HybCycle_15/MMStack_Pos1.ome.tif'
    analysis_name = 'jina_pseudos_4_corrected_2_pos_2_chs_pil_load_strict_2_only_blur_thresh_60'
    side_by_side_preprocess_checks(tiff_src, analysis_name)
                
            
        
        
        
        
        
        
        
        
        
        
        
        
        