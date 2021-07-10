function [tform, threshold] = beadtformbypos(beadImDir, position)
% grabs tform for each channel
%
% Assumes the images are named 'MMStack_Pos0.ome.tif' where position number
% varies
%
% Dependencies; 
% Fiji Path
% addpath('C:\Users\Long Cai - 2\Desktop\Fiji.app\scripts\', '-end'); 
% bfmatlab path to open images
% addpath('C:\github\streamline-seqFISH\src\process_with_beads\bfmatlab\');

% make new function to get only chromatic aberrations


    %% initial variables
    typedots = 'log';
    
    %% get the images
    beadImDir = fullfile(beadImDir, ['MMStack_Pos' num2str(position) '.ome.tif']);
    [I, sizeC, sizeZ, ~] = grabimseries(beadImDir, position);
    
    %% Calculate the autothreshold
    threshold = ones(1, sizeC) * 99999;
    points = cell(1, sizeC);
    for ch = 1:sizeC
        logFish = max(I{ch},[],3);
        thresh = multithresh(logFish,2);
        if thresh < 550
            thresh = threshold(ch-1);
        end
        threshold(ch) = thresh(2);
        [points{ch}, ~, ~, ~] = detectdotsv2(I{ch}, threshold(ch), typedots);
    end

    %% All points are in all channels
    tform = cell(sizeC, 1);
    for ch = 1:sizeC
        tform{ch} = getglobaltform(points{1},points{ch});
    end

end