function [tform] = full_wrap_alignment(fixed_src, moving_src, dst, varargin)
    
    %Read in Tiff src s
    %-----------------------------------------------------------------
    fixed_src
    moving_src
    disp('Importing Images')
    get_pos_from_path(fixed_src)
    fixed = loadometiff(fixed_src, get_pos_from_path(fixed_src));
    moving = loadometiff(moving_src, get_pos_from_path(moving_src));
    
    size(fixed)
    size(moving)
    
    size_moving = size(moving)
    if size_moving(2) == 1
        moving = permute(moving, [2,1,3,4]);
    end
    
    size(moving)
    %-----------------------------------------------------------------
    
    %Get last dapi channel
    %-----------------------------------------------------------------
    disp('Getting Dapis')
    fixed_dapi = squeeze(fixed(:,end,:,:));
    moving_dapi = squeeze(moving(:,end,:,:));
    %-----------------------------------------------------------------
    
    size_of_len = size(size(fixed_dapi))
    if size_of_len(2) == 2
        fixed_dapi = cat(3, fixed_dapi, fixed_dapi);
        moving_dapi = cat(3, moving_dapi, moving_dapi);
    
    else
        moving_dapi = permute(moving_dapi, [2,3,1]);
        fixed_dapi = permute(fixed_dapi, [2,3,1]);
    end
    
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