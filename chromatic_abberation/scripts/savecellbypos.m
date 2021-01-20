function [] = savecellbypos(hybIms, saveDir, startString, endingString)
% saves the tif images in a cell array, only grabbing each cell and 5
% zslices from each image.
%
% Date: 3/5/2020
% Author: Nico Pierson
% Email: nicogpt@caltech.edu

    %% Reorganize images so only 20 channels are saved each time
    numChannels = size(hybIms,2);
    numPos = size(hybIms, 1) * numChannels;
    if numChannels > 1
        Iorg = cell(numPos, 1);
        for f = 1:size(hybIms, 1)
            for ch = 1:numChannels
                hybIndex = (f-1) * numChannels + ch;
                Iorg{hybIndex} = hybIms{f,ch};
            end
        end
        hybIms = Iorg;
        clearvars Iorg
    end


    %% Need to save the images per barcode round for each channel
    Miji(false);
    numPos = size(hybIms,1);
    numImagesPerFile = 21;
    numZSlice = size(hybIms{1}, 3);
    numSplits = ceil(numPos / numImagesPerFile);
    baseArray = 1:numImagesPerFile;

    for split = 1:numSplits
        leftImages = mod(numPos, numImagesPerFile);
        if split ~= numSplits || leftImages == 0
            splitArray = baseArray + (numImagesPerFile * (split - 1)); % use array to split...
        else
            splitArray = (1 + (numImagesPerFile * (split-1))):(leftImages + numImagesPerFile * (split - 1));
        end
        numChannelsInImage = length(splitArray);
        
        iter = 1;
        for f = splitArray
            namesh{iter} = ['C' num2str(split) '-'  num2str(f) '.tif'];
            MIJ.createImage(namesh{iter}, hybIms{f}, true);
            iter = iter + 1;
        end


        %% Need to break up the images, because there are too many, break into 4 separate images
        str = [];
        iter = 1;
        for f = splitArray
            str = [str ' image' num2str(iter) '=C' num2str(split) '-' num2str(f) '.tif'];
            iter = iter + 1;
        end

  
        try
            if numPos > 1
                MIJ.run('Concatenate...', ['  title=[Concatenated Stacks] open' str]);
            end
            MIJ.run('Stack to Hyperstack...', ['order=xyzct channels=' num2str(numChannelsInImage) ' slices=' num2str(numZSlice) ' frames=1 display=Grayscale']);
            savePath = fullfile(saveDir, [startString '-pos0_' num2str(numPos) '-' endingString]);
            MIJ.run('Save', ['save=[' savePath '.tif' ']']);
            MIJ.run('Close All')
        catch
            MIJ.exit;
            error('MIJ exited incorrectly: most likely caused by out of memory in the java heap\n');
        end
    end
end