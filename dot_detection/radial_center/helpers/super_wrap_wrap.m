function [radPoints, radInt] = super_wrap_wrap(tiff_path, channel_num, points_path, radPoints_dst)
% getgaussian gets points and returns gaussian fit points
%
% Author: Nico Pierson
% Date: 4/4/2019
% Email: nicogpt@caltech.edu
% Modified:
    
    %Get Image
    %---------------------------------------------
    tiff = loadometiff(tiff_path,0);
    
    channel_matlab = channel_num + 1;
    
    image_unorganized = squeeze(tiff(:,channel_matlab,:,:));
    
    image = permute(image_unorganized, [3,2,1]);
    %---------------------------------------------
   
    %Get Normal Points
    %---------------------------------------------
    points_mat = load(points_path);
    points = double(points_mat.points) + 1;
    %---------------------------------------------
    
    
    %Get Rad Points
    %---------------------------------------------
    [radPoints, radInt] = SuperResPoints(points, image,1,1);
    %---------------------------------------------
    
    %Save Rad Points
    %---------------------------------------------
    save(radPoints_dst, 'radPoints', 'radInt');
    %---------------------------------------------
end
