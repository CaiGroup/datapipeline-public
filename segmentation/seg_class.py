import os
import json
import sys
import scipy.io as sio
import numpy as np
import glob
import tifffile as tf
sys.path.insert(0, os.getcwd())


#Segmentation Script
#----------------------------
from segmentation.roi_segment import run_roi
from segmentation.cellpose_segment import run_cellpose
from segmentation.post_processing.get_post_processing import save_labeled_img
from segmentation.visualization.visual_seg import get_label_img_visuals
from segmentation.cellpose_segment.helpers.combine_count_matrices import get_count_matrix_for_pos
from post_analyses.gene_to_gene_corr_matrix import get_gene_to_gene_correlations
#----------------------------

#On Off Barcode plot function
#----------------------------
from helpers.combine_position_results.on_off_barcode_plot_all_pos import get_on_off_barcode_plot_all_pos
#----------------------------

main_dir = '/groups/CaiLab'

#Analysis Class to set and run parameters for analyses
#=====================================================================================
class Segmentation:
    def __init__(self, data_dir, position, seg_dir, decoded_dir, locations_dir, barcode_dst, barcode_src,
                    bool_fake_barcodes, bool_decoding_individual, num_z_slices, seg_type, seg_data_dir, dimensions, num_zslices,
                    labeled_img, edge_dist, dist_between_nuclei, bool_cyto_match, area_tol, cyto_channel_num,
                    get_nuclei_img, get_cyto_img, num_wav, nuclei_radius, flow_threshold, cell_prob_threshold,
                    nuclei_channel_num, cyto_flow_threshold, cyto_cell_prob_threshold, cyto_radius):

        self.data_dir = data_dir
        self.position = position
        self.seg_dir = seg_dir
        self.locations_dir = locations_dir
        self.decoded_dir = decoded_dir
        self.barcode_dst = barcode_dst
        self.barcode_src = barcode_src
        self.fake_barcodes = bool_fake_barcodes
        self.decoding_individual = bool_decoding_individual
        self.num_z_slices = num_z_slices
        self.seg_type = seg_type.lower()
        self.seg_dir = seg_dir
        self.seg_data_dir = seg_data_dir
        self.dimensions = dimensions
        self.num_zslices = num_zslices
        self.labeled_img = labeled_img
        self.edge_dist = edge_dist
        self.dist_between_nuclei = dist_between_nuclei
        self.bool_cyto_match = bool_cyto_match
        self.area_tol = area_tol
        self.cyto_channel_num = cyto_channel_num
        self.get_nuclei_img = get_nuclei_img
        self.get_cyto_img = get_cyto_img
        self.labeled_img = labeled_img
        self.num_wav = num_wav
        self.nuclei_radius = nuclei_radius
        self.flow_threshold = flow_threshold
        self.cell_prob_threshold = cell_prob_threshold
        self.nuclei_channel_num = nuclei_channel_num
        self.cyto_flow_threshold = cyto_flow_threshold
        self.cyto_cell_prob_threshold = cyto_cell_prob_threshold
        self.cyto_radius = cyto_radius

    def combine_seg_z_s(seg_channel_dir):

        #Get Csv's
        #-----------------------------------------------------
        glob_me = os.path.join(seg_channel_dir, '*', 'gene_locations_assigned_to_cell.csv')

        csv_s = glob.glob(glob_me)

        assert len(csv_s) > 0, "There are no csv's in the Z Slices for segmentation"
        #-----------------------------------------------------


        #Concatenate Csv's
        #-----------------------------------------------------
        df_concat = pd.read_csv(csv_s[0])

        for i in range(1, len(csv_s)):
            df_concat_me = pd.read_csv(csv_s[i])

            df_concat = pd.concat([df_concat, df_concat_me])
        #-----------------------------------------------------


        #Save Concatenated Csv
        #-----------------------------------------------------
        concat_dst = os.path.join(seg_channel_dir, 'gene_locations_assigned_to_cell.csv')
        df_concat.to_csv(concat_dst, index=False)
        #-----------------------------------------------------


    def run_segmentation_across(self):

        # Get Segmentation DIrs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------

        #Get Decoded genes path
        #----------------------------------------------
        decoded_genes_glob = os.path.join(self.decoded_dir, '*unfiltered.csv')

        decoded_genes_paths = glob.glob(decoded_genes_glob)

        assert len(decoded_genes_paths) == 1, "There should be exactly one file with *unfiltered.csv"

        decoded_genes_path = decoded_genes_paths[0]
        #----------------------------------------------
        
        #Get Barcode csv
        #----------------------------------------------
        barcode_key_src = os.path.join(self.barcode_dst, 'barcode.csv')
        #----------------------------------------------
        
        #If Roi
        #----------------------------------------------
        if 'roi' in self.seg_type:

            #Set Directory args
            #----------------------------------------------
            glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')

            roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)

            assert len(roi_zip_file_paths) == 1

            roi_zip_file_path = roi_zip_file_paths[0]

            barcode_path = os.path.join(self.barcode_src, 'barcode.csv')
            #----------------------------------------------

            run_roi.run_me(self.seg_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes, self.num_zslices)
             #----------------------------------------------

        elif "cellpose" in self.seg_type:
            run_cellpose.run_me(self.data_dir, self.seg_dir, decoded_genes_path, barcode_key_src, self.position, self.labeled_img)

            #----------------------------------------------

    def run_segmentation_non_barcoded(self):

        # Get Segmentation DIrs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------

        #Get Decoded genes path
        #----------------------------------------------
        decoded_genes_path = os.path.join(self.decoded_dir, 'sequential_decoding_results.csv')
        #----------------------------------------------

        #Get Barcode Key src
        #----------------------------------------------
        barcode_key_src = os.path.join(self.barcode_dst, 'sequential_key.csv')
        print(f'{barcode_key_src=}')
        #----------------------------------------------


        run_cellpose.run_me(self.data_dir, self.seg_dir, decoded_genes_path, barcode_key_src, self.position, self.labeled_img)



    def run_segmentation_individually(self):


        # Get Segmentation Dirs
        #----------------------------------------------
        for channel_num in self.decoding_individual:

            # Get Segmentation Dirs
            #----------------------------------------------
            segmented_dir = os.path.join(self.seg_dir, 'Channel_'+str(channel_num))
            os.makedirs(segmented_dir, exist_ok=True)
            #----------------------------------------------

            #Get Decoded genes path
            #----------------------------------------------
            decoded_genes_glob = os.path.join(self.decoded_dir, 'Channel_'+str(channel_num),'*unfiltered.csv')
            decoded_genes_paths = glob.glob(decoded_genes_glob)
            print(f'{decoded_genes_glob=}')
            assert len(decoded_genes_paths) == 1, "There should be exactly one file with *unfiltered.csv"
            decoded_genes_path = decoded_genes_paths[0]
            #----------------------------------------------

            #Get Barcode key src
            #----------------------------------------------
            barcode_key_src = os.path.join(self.barcode_dst, 'channel_' + str(channel_num) + '.csv')
            print(f'{barcode_key_src=}')
            #----------------------------------------------


            if 'roi' in self.seg_type:

                barcode_path = os.path.join(self.barcode_src, 'channel_' +str(channel_num)+'.csv')
                #----------------------------------------------
                glob_me_for_roi_zips = os.path.join(self.seg_data_dir, '*')

                roi_zip_file_paths = glob.glob(glob_me_for_roi_zips)

                assert len(roi_zip_file_paths) == 1

                roi_zip_file_path = roi_zip_file_paths[0]
                #----------------------------------------------
                run_roi.run_me(segmented_dir, decoded_genes_path, barcode_path, roi_zip_file_path, self.fake_barcodes,  self.num_zslices)

            elif "cellpose" in self.seg_type:

                print(f'{self.labeled_img.shape=}')

                run_cellpose.run_me(self.data_dir, segmented_dir, decoded_genes_path, barcode_key_src, self.position, self.labeled_img)
                #----------------------------------------------

        #Get count matrix for positions
        #----------------------------------------------
        pos_count_matrix_dst = os.path.join(self.seg_dir, 'count_matrix_all_channels.csv')
        get_count_matrix_for_pos(self.seg_dir, pos_count_matrix_dst)
        #----------------------------------------------

        #Get Gene Correlation matrix for position
        #----------------------------------------------
        get_gene_to_gene_correlations(pos_count_matrix_dst, self.seg_dir)
        #----------------------------------------------

        #Get On/Off Barcode plot
        #----------------------------------------------
        on_off_barcode_plot_dst = os.path.join(self.seg_dir, 'on_off_barcode_plot_all_channels_in_position.png')
        get_on_off_barcode_plot_all_pos(pos_count_matrix_dst, on_off_barcode_plot_dst)
        #----------------------------------------------

    def retrieve_labeled_img(self):
        # Get Segmentation Dirs
        #----------------------------------------------
        if not os.path.exists(self.seg_dir):
            os.makedirs(self.seg_dir)
        #----------------------------------------------

        label_img_path = save_labeled_img(self.data_dir, self.seg_dir, self.position, self.edge_dist, self.dist_between_nuclei,
            self.bool_cyto_match, self.area_tol, self.cyto_channel_num, self.get_nuclei_img, self.get_cyto_img, self.num_wav,
            self.nuclei_radius, self.num_zslices, self.flow_threshold, self.cell_prob_threshold, self.nuclei_channel_num,
            self.cyto_flow_threshold, self.cyto_cell_prob_threshold, self.cyto_radius)

        print(f'{label_img_path=}')
        # get_label_img_visuals(label_img_path, self.data_dir, self.position, self.num_wav)

        labeled_img = tf.imread(label_img_path)

        return labeled_img

if sys.argv[1] == 'debug_seg_class_indiv':
    labeled_img_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_mult_ch/MMStack_Pos0/Segmentation/labeled_img_post.tif'

    labeled_img = tf.imread(labeled_img_src)
    segmenter = Segmentation(data_dir = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/',
                            position = 'MMStack_Pos.ome.tif',
                            seg_dir = 'foo/seg_test',
                            decoded_dir = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Decoded',
                            locations_dir ='/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/MMStack_Pos1/Dot_Locations',
                            barcode_dst = '/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_6/BarcodeKey',
                            barcode_src = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/barcode_key',
                            bool_fake_barcodes = True,
                            bool_decoding_individual = [1],
                            num_z_slices = None,
                            seg_type = 'cellpose',
                            seg_data_dir = '/central/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/segmentation',
                            dimensions = 3,
                            num_zslices = 3,
                            labeled_img = labeled_img,
                            edge_dist = 0,
                            dist_between_nuclei = 0,
                            bool_cyto_match= False,
                            area_tol = False,
                            cyto_channel_num = False,
                            get_nuclei_img = True,
                            get_cyto_img = False,
                            num_wav = 4,
                            nuclei_radius = 0,
                            flow_threshold = .4,
                            cell_prob_threshold = 0,
                            nuclei_channel_num = -1,
                            cyto_flow_threshold = 0,
                            cyto_cell_prob_threshold =0,
                            cyto_radius =0)
    print("Created Segmentation Class")

    segmenter.run_segmentation_individually()

if sys.argv[1] == 'debug_seg_class_multiple_indiv':
    labeled_img_src = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos1/Segmentation/labeled_img_post.tif'

    labeled_img = tf.imread(labeled_img_src)
    segmenter = Segmentation(data_dir = '/central/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_4_corrected/',
                            position = 'MMStack_Pos.ome.tif',
                            seg_dir = 'foo/seg_test',
                            decoded_dir = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos1/Decoded',
                            locations_dir ='/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/MMStack_Pos1/Dot_Locations',
                            barcode_dst = '/groups/CaiLab/analyses/nrezaee/jina_1_pseudos_4_corrected/jina_pseudos_4_corrected_all_pos_all_chs_pil_load_strict_2_only_blur_thresh_60/BarcodeKey',
                            barcode_src = '/central/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_4_corrected/barcode_key',
                            bool_fake_barcodes = True,
                            bool_decoding_individual = [1,2,3],
                            num_z_slices = None,
                            seg_type = 'cellpose',
                            seg_data_dir = '/central/groups/CaiLab/personal/nrezaee/raw/jina_1_pseudos_4_corrected/segmentation',
                            dimensions = 3,
                            num_zslices = 3,
                            labeled_img = labeled_img,
                            edge_dist = 0,
                            dist_between_nuclei = 0,
                            bool_cyto_match= False,
                            area_tol = False,
                            cyto_channel_num = False,
                            get_nuclei_img = True,
                            get_cyto_img = False,
                            num_wav = 4,
                            nuclei_radius = 0,
                            flow_threshold = .4,
                            cell_prob_threshold = 0,
                            nuclei_channel_num = -1,
                            cyto_flow_threshold = 0,
                            cyto_cell_prob_threshold =0,
                            cyto_radius =0)
    print("Created Segmentation Class")

    segmenter.run_segmentation_individually()

if sys.argv[1] == 'debug_seg_class_non_barcoded':
    labeled_img_src = '/groups/CaiLab/analyses/Michal/2021-05-20_P4P5P7_282plex_Neuro4196_5/michal_mult_ch/MMStack_Pos0/Segmentation/labeled_img_post.tif'

    labeled_img = tf.imread(labeled_img_src)
    segmenter = Segmentation(data_dir = '/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013',
                            position = 'MMStack_Pos1.ome.tif',
                            seg_dir = 'foo/seg_test_non_barcoded',
                            decoded_dir = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Decoded',
                            locations_dir ='/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/MMStack_Pos1/Dot_Locations',
                            barcode_dst = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/BarcodeKey',
                            barcode_src = '/groups/CaiLab/analyses/alinares/2021_0607_control_20207013/smfish_test/barcode_key',
                            bool_fake_barcodes = True,
                            bool_decoding_individual = [1],
                            num_z_slices = None,
                            seg_type = 'cellpose',
                            seg_data_dir = '/groups/CaiLab/personal/alinares/raw/2021_0607_control_20207013/segmentation',
                            dimensions = 3,
                            num_zslices = 3,
                            labeled_img = labeled_img,
                            edge_dist = 0,
                            dist_between_nuclei = 0,
                            bool_cyto_match= False,
                            area_tol = False,
                            cyto_channel_num = False,
                            get_nuclei_img = True,
                            get_cyto_img = False,
                            num_wav = 4,
                            nuclei_radius = 0,
                            flow_threshold = .4,
                            cell_prob_threshold = 0,
                            nuclei_channel_num = -1,
                            cyto_flow_threshold = 0,
                            cyto_cell_prob_threshold =0,
                            cyto_radius =0)
    print("Created Segmentation Class")

    segmenter.run_segmentation_non_barcoded()


if sys.argv[1] == 'debug_seg_class_across':
    labeled_img_src = '/groups/CaiLab/analyses/Lex/20k_dash_063021_3t3/lex_bug3/MMStack_Pos0/Segmentation/labeled_img_post.tif'
    
    labeled_img = tf.imread(labeled_img_src)
    segmenter = Segmentation(data_dir = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3/', 
                            position = 'MMStack_Pos0.ome.tif', 
                            seg_dir = 'foo/seg_test_across', 
                            decoded_dir = '/groups/CaiLab/analyses/Lex/20k_dash_063021_3t3/lex_bug3/MMStack_Pos0/Decoded', 
                            locations_dir ='//groups/CaiLab/analyses/Lex/20k_dash_063021_3t3/lex_bug3/MMStack_Pos0/Dot_Locations', 
                            barcode_dst = '/groups/CaiLab/analyses/Lex/20k_dash_063021_3t3/lex_bug3/BarcodeKey', 
                            barcode_src = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3/barcode_key/barcode_key', 
                            bool_fake_barcodes = True,
                            bool_decoding_individual = [1], 
                            num_z_slices = None,
                            seg_type = 'cellpose', 
                            seg_data_dir = '/groups/CaiLab/personal/Lex/raw/20k_dash_063021_3t3/segmentation/', 
                            dimensions = 3, 
                            num_zslices = 3, 
                            labeled_img = labeled_img, 
                            edge_dist = 0, 
                            dist_between_nuclei = 0, 
                            bool_cyto_match= False, 
                            area_tol = False, 
                            cyto_channel_num = False, 
                            get_nuclei_img = True, 
                            get_cyto_img = False, 
                            num_wav = 4, 
                            nuclei_radius = 0, 
                            flow_threshold = .4, 
                            cell_prob_threshold = 0,
                            nuclei_channel_num = -1, 
                            cyto_flow_threshold = 0, 
                            cyto_cell_prob_threshold =0, 
                            cyto_radius =0)
    print("Created Segmentation Class")
    
    segmenter.run_segmentation_across()

                