#!/bin/bash 
  matlab -r "addpath('/home/nrezaee/test_cronjob_multi_dot/decoding/helpers');main_decoding('/groups/CaiLab/analyses/nrezaee/2020-08-08-takei/takei_strict_8/BarcodeKey/channel_1.mat', 'foo/test_decoding_class/Channel_1/cell_33/locations_for_cell.csv', 'foo/test_decoding_class/Channel_1/cell_33', 4, 64, 1, 1, None, 'None'); quit"; 