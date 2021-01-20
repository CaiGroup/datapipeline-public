function [tform] = full_wrap_alignment(fixed_src, moving_src, dst, varargin)


    disp('Importing Images')
    fixed = loadometiff(fixed_src, 0);
    moving = loadometiff(moving_src, 0);
    
    disp('Getting Dapis')
    fixed_dapi = squeeze(fixed(:,end,:,:));
    moving_dapi = squeeze(moving(:,end,:,:));
    
    moving_dapi = permute(moving_dapi, [2,3,1]);
    fixed_dapi = permute(fixed_dapi, [2,3,1]);
    
    size(fixed_dapi)
    size(moving_dapi)
    
    disp('Running Alignment')
    [tform, imageCheck] = grabtform(moving_dapi, fixed_dapi);
    
    offset = tform.T(4,1:3)
    
    writematrix(offset, dst)
end

% moving_src= 'moving.tif'
% fixed_src= 'fixed.tif'
% full_wrap(fixed_src, moving_src, tform_dst)