addpath('bfmatlab')

disp('Importing Images')
fixed = loadometiff('fixed.tif');
moving = loadometiff('moving.tif');

disp('Getting Dapis')
fixed_dapi = squeeze(fixed(:,3,:,:));
moving_dapi = squeeze(moving(:,3,:,:));

disp('Running Alignment')
[tform, imageCheck] = grabtform(moving_dapi,fixed_dapi)