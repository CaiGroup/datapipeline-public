function [gaussPoints, gaussInt] = getgaussian_wrap(tiff_path, channel_num, points_path, gaussian_dst)
% getgaussian gets points and returns gaussian fit points
%
% Author: Nico Pierson
% Date: 4/4/2019
% Email: nicogpt@caltech.edu
% Modified:

    tiff = loadometiff(tiff_path,0);
    
    channel_num_matlab = channel_num +1
    image_unorganized = squeeze(tiff(:,channel_num_matlab,:,:));
    
    image = permute(image_unorganized, [3,2,1]);
    
    points_info = load(points_path);
    points = double(points_info.points) + 1;

    
    [gaussPoints, gaussInt] = getgaussian(points, image);
   
    gaussian_dst
    save(gaussian_dst, 'gaussPoints', 'gaussInt')
end
