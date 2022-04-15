import os

import pandas as pd


def combine_locs(rand_list):
    check_if_first_tiff = 0
    temp_dir = '/groups/CaiLab/personal/temp/temp_dots'
    for rand in rand_list:
        print(temp_dir, rand)
        locs_src = os.path.join(temp_dir, rand, 'locs.csv')

        df_tiff = pd.read_csv(locs_src)

        if check_if_first_tiff == 0:
            df_all = df_tiff
            print(f'{df_all.shape=}')

            check_if_first_tiff += 1
        else:

            df_all = df_all.append(df_tiff)
            print(f'{df_all.shape=}')

    return df_all
