addpath('C:\Users\zrezaee\Documents\cai-lab\dot_detection\matlab_3d\bfmatlab\bfmatlab')

tiff = loadometiff('mini_tiff1.tif');
tiff_3d = squeeze(tiff(:,1,:,:));

tiff_3d = permute(tiff_3d, [3 2 1]);
[dots, intensity, dotsLogical, logImage] = detectdotsv2(tiff_3d, 1000, 'exons',1, 'foo');