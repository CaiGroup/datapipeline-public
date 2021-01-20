
addpath('bfmatlab/bfmatlab')

tiff_src = 'MMStack_Pos0.ome.tif';


nbins = 110;
strictness = 3;

threshold = 1000;
channel =1;
[dots, thresh_ints] = biggest_jump(tiff_src, channel, threshold, nbins, strictness);
size(dots)
size(thresh_ints)