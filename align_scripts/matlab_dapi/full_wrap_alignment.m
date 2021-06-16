function [tform] = full_wrap_alignment(fixed_src, moving_src, dst, varargin)

    fixed_src
    moving_src
    disp('Importing Images')
    get_pos_from_path(fixed_src)
    fixed = loadometiff(fixed_src, get_pos_from_path(fixed_src));
    moving = loadometiff(moving_src, get_pos_from_path(fixed_src));
    
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