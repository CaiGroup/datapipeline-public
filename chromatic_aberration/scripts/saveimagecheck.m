function [] = saveimagecheck(imageCheck, savePath)
% saves the tif images used as alignment checks, save only 5 zslices in
% the middle of the tif file
%
% Date: 3/20/2020
% Author: Nico Pierson
% Email: nicogpt@caltech.edu

            
    %% Reorganize images so only 20 channels are saved each time
    numZ = 5; % use 5 zslices
    Miji(false);
    numImages = length(imageCheck);
    numZSlice = size(imageCheck{1}, 3);
    
    %% get specific zslices from the middle of the zStack
    if numZSlice < 5
        zStep = 0;
    else
        zStep = floor(numZ / 2);
    end
    mid = ceil(numZSlice / 2);
    zStart = mid - zStep;
    zEnd = mid + zStep;
    zIdx = zStart:zEnd;

    iter = 1;
    for f = 1:numImages
        namesh{iter} = ['C' num2str(f) '-'  num2str(1) '.tif'];
        MIJ.createImage(namesh{iter}, imageCheck{f}(:,:,zIdx), true);
        iter = iter + 1;
    end


    %% Need to break up the images, because there are too many, break into 4 separate images
    str = [];
    iter = 1;
    for f = 1:numImages
        str = [str ' image' num2str(iter) '=C' num2str(f) '-' num2str(1) '.tif'];
        iter = iter + 1;
    end


    try
        if numImages > 1
            MIJ.run('Concatenate...', ['  title=[Concatenated Stacks] open' str]);
        end
        MIJ.run('Stack to Hyperstack...', ['order=xyzct channels=' num2str(numImages) ' slices=' num2str(length(zIdx)) ' frames=1 display=Grayscale']);
        MIJ.run('Save', ['save=[' savePath ']']);
        MIJ.run('Close All')
    catch
        MIJ.exit;
        error('MIJ exited incorrectly: most likely caused by out of memory in the java heap\n');
    end

end