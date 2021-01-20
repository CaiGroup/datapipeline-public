
addpath('bfmatlab')

tiff_path = 'MMStack_Pos0.ome.tif'

points = randi([8 10],5,3)

points_path = 'points.mat'
save(points_path, points)

path_to_save_


channel_num = 1

dst='results'

getgaussian_wrap(tiff_path, channel_num, points_path, dst)

