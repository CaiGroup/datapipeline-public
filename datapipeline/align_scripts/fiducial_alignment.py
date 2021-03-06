import os
import sys

import pandas as pd

from datapipeline.align_scripts.fiducial_marker_helpers.FMAligner import FMAligner
from datapipeline.align_scripts.fiducial_marker_helpers.colocalize_dots import get_colocs
from datapipeline.align_scripts.fiducial_marker_helpers.fid_alignment_check import plot_hyb_locs_on_fids
from datapipeline.align_scripts.fiducial_marker_helpers.get_fiducial_dots_in_tiff_top import get_dots_for_tiff_top


def get_fiducial_offset(data_dir, position, dst_dir, locs_src, num_wav):
    # Get Paths of fiducials
    # ----------------------------------------------------------------------------
    fid_init_path = os.path.join(data_dir, 'initial_fiducials', position)
    fid_final_path = os.path.join(data_dir, 'final_fiducials', position)
    # ----------------------------------------------------------------------------

    # Run Dot Detection
    # ----------------------------------------------------------------------------
    final_fids_dst_dir = os.path.join(dst_dir, 'final_fids')
    initial_fids_dst_dir = os.path.join(dst_dir, 'initial_fids')
    df_fid_final = get_dots_for_tiff_top(fid_final_path, num_wav, final_fids_dst_dir, dot_radius=2)
    df_fid_init = get_dots_for_tiff_top(fid_init_path, num_wav, initial_fids_dst_dir, dot_radius=2)
    # ----------------------------------------------------------------------------

    # Colocalize Initial and Final
    # ----------------------------------------------------------------------------
    df_fid_final, df_fid_init = get_colocs(os.path.join(final_fids_dst_dir, 'locs.csv'),
                                           os.path.join(initial_fids_dst_dir, 'locs.csv'))
    # ----------------------------------------------------------------------------

    print(f'{df_fid_final.shape}')
    print(f'{df_fid_init.shape=}')

    # Plot Hyb Locs on Fids
    # ----------------------------------------------------------------------------
    hyb_locs_on_fids_dst = os.path.join(dst_dir, 'Hyb_Dots_On_Fid_Dots_Check.png')
    plot_hyb_locs_on_fids(locs_src, os.path.join(final_fids_dst_dir, 'locs.csv'),
                          os.path.join(initial_fids_dst_dir, 'locs.csv'), hyb_locs_on_fids_dst)
    # ----------------------------------------------------------------------------

    # Read in points
    # ----------------------------------------------------------------------------
    df_points = pd.read_csv(locs_src)
    # ----------------------------------------------------------------------------

    # Loop through channels
    # ----------------------------------------------------------------------------
    channels = list(range(1, int(num_wav) + 1))
    for channel in channels:
        # Set Inputs
        # ----------------------------------------------------------------------------
        ch_ref = df_fid_init.set_index("ch").loc[channel]
        ch_ro = df_points.set_index("ch").loc[channel].set_index("hyb")
        ch_ref_final = df_fid_final.set_index("ch").loc[channel]
        # ----------------------------------------------------------------------------

        # Run Fiducial Alignment
        # ----------------------------------------------------------------------------
        dal = FMAligner(ch_ro, ch_ref, ch_ref_final)
        dal.auto_set_params()
        dal.align()
        # ----------------------------------------------------------------------------

        # Save Offsets
        # ----------------------------------------------------------------------------
        dal.save_offsets(os.path.join(dst_dir, "offsets_ch" + str(channel) + ".csv"))
        dal.save_matches(os.path.join(dst_dir, "matches_ch" + str(channel) + ".csv"))
        dal.save_loocv_errors(os.path.join(dst_dir, "loov_errors_ch" + str(channel) + ".csv"))
        # ----------------------------------------------------------------------------


if __name__ == '__main__':

    if sys.argv[1] == 'debug_fiducials':
        sys.path.insert(0, os.getcwd())
        data_dir = '/groups/CaiLab/personal/nrezaee/raw/2020-10-19-takei/'
        position = 'MMStack_Pos0.ome.tif'
        locs_src = '/groups/CaiLab/analyses/nrezaee/2020-10-19-takei/takei_fid/MMStack_Pos0/Dot_Locations/locations.csv'
        dst_dir = 'foo/test_fid_alignment2'

        os.makedirs(dst_dir, exist_ok=True)

        num_wav = 4
        get_fiducial_offset(data_dir, position, dst_dir, locs_src, num_wav)

    
