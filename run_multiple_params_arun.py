import os
import sys
from decoding.syndrome_decoding import run_syndrome_decoding

dst_dir = '/groups/CaiLab/personal/nrezaee/synd_decoding/multiple_params_arun'
os.makedirs(dst_dir, exist_ok=True)

z_var_factor = 20
for lat_var_factor in range(10,50,20):
    for lw_var_factor in range(1, 3):
        specific_dst_dir = os.path.join(dst_dir, 'lat_var_' + str(lat_var_factor) + '_lw_var_' + str(lw_var_factor) + '_z_var_' + str(z_var_factor))
        print(f'{specific_dst_dir=}')
        os.makedirs(specific_dst_dir, exist_ok=True)
        run_syndrome_decoding(barcode_src= '/groups/CaiLab/personal/nrezaee/raw/arun_auto_testes_1/barcode_key/channel_1.csv',
                              locations_src='/groups/CaiLab/analyses/nrezaee/arun_auto_testes_1/arun_testes_ch1_strict_0/MMStack_Pos2/Dot_Locations/locations.csv',
                              dst_dir = specific_dst_dir,
                              bool_fake_barcodes = True,
                              lat_var_factor=lat_var_factor,
                              z_var_factor=z_var_factor, 
                              lw_var_factor=lw_var_factor)
