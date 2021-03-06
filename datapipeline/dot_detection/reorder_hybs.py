from __future__ import annotations

import glob


def get_and_sort_hybs(path_to_experiment_dir):
    # Get all files in path
    # -------------------------------------------------
    hyb_dirs = glob.glob(path_to_experiment_dir)
    # -------------------------------------------------

    # Remove anything that is not a Hyb
    # -------------------------------------------------
    hyb_dirs = [hyb_dir for hyb_dir in hyb_dirs if 'Hyb' in hyb_dir]
    # -------------------------------------------------

    # Split hybs to get numbers
    # -------------------------------------------------
    split_word = 'Cycle_'
    for index in range(len(hyb_dirs)):
        hyb_dirs[index] = hyb_dirs[index].split(split_word)

        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    # -------------------------------------------------

    # Sort the Hybs
    # -------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    # -------------------------------------------------

    # Combine the strings to right format
    # -------------------------------------------------
    for index in range(len(sorted_hyb_dirs)):
        sorted_hyb_dirs[index][1] = str(sorted_hyb_dirs[index][1])
        sorted_hyb_dirs[index].insert(1, split_word)
        sorted_hyb_dirs[index] = ''.join(sorted_hyb_dirs[index])
    # -------------------------------------------------

    return sorted_hyb_dirs
