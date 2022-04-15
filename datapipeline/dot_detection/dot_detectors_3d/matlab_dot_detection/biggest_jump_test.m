
addpath('bfmatlab/bfmatlab')

tiff_src = '/groups/CaiLab/personal/nrezaee/raw/2020-08-08-takei/HybCycle_21/MMStack_Pos0.ome.tif';


nbins = 110;
strictness = 5;

threshold = 600;
channel =1;
[dots, thresh_ints] = biggest_jump(tiff_src, channel, threshold, nbins, strictness, 'foo.mat');
size(dots)
size(thresh_ints)