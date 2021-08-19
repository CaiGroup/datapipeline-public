function globaltform = beadtformglobal(beadImDir, numChannels, posArray, t_form_dest)
% wrapper function to get global tform for all positions
% posArray = [0,1,2, 3]
% numChannels=4
% 
% inputs: bead image directory, number of channels, position array (usually
% starts from 0)
%
% outputs: average global tform cell array from every position
%
% Assumes the images are named 'MMStack_Pos0.ome.tif' where position number
% varies
%
% Dependencies; 
% Fiji Path
% addpath('C:\Users\Long Cai - 2\Desktop\Fiji.app\scripts\', '-end'); 
% bfmatlab path to open images
% addpath('C:\github\streamline-seqFISH\src\process_with_beads\bfmatlab\');

    % variables
    numPositions = length(posArray);
    
    %% All points are in all channels
    tform = cell(numPositions, 1);
    iter = 1;
    for position = posArray
        tform{iter} = beadtformbypos(beadImDir, position);
        iter = iter + 1;
    end
    
    % organize the tforms by channel
    tformmat = cell(numPositions,1);
    for ch = 1:numPositions
        for pos = 1:numPositions
            tformmat{ch}(:,:,pos) = tform{pos}{ch}.T; 
        end
    end
    
    
    % get average and add to global tform cell array
    fprintf('Global Tform Average for all positions:\n');
    globaltform = cell(numPositions,1);
    for ch = 1:numChannels
        fprintf('ch%.0f:\n', ch);
        tformAvg = mean(tformmat{ch}, 3)
        globaltform{ch} = (tformAvg);
    end
    
    t_forms_file_path = fullfile(t_form_dest, 't_form_variables.mat')
    
    disp(class(t_forms_file_path))
    
    save(convertCharsToStrings(t_forms_file_path))      
    
end