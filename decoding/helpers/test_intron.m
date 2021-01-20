locations_src = '/groups/CaiLab/analyses/nrezaee/intron_pos0/decoding_slurm/MMStack_Pos0/locations.mat'

barcode_src = '/groups/CaiLab/analyses/nrezaee/intron_pos0/decoding_slurm/barcode.mat'

dest = '/home/nrezaee/sandbox' 

num_of_rounds = 5;

total_num_of_channels =12;

main_decoding(barcode_src, locations_src, dest, num_of_rounds, total_num_of_channels)  