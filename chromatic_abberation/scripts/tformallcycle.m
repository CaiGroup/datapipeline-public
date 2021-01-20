function [tform, imageCheck] = tformallcycle(experimentDir, refDir, position, ...
    hybcycleArray, varargin)
% wrapper function to get all the tforms in the experiment for all the
% hybcycle folders in each position
%
% folder names assumed to be 'HybCycle_[0-9]'
%
% optional arg: channel is the channel to align, e.g. 1 or 2, 'dapi' for
% the last channel
%
% image assumed to be 'MMStack_Pos[0-9].ome.tif'



    %% Set up optional Parameters
    argsLimit = 2;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('myfun:tformallpos:TooManyInputs', ...
            'requires at most 2 optional inputs');
    end
    optargs = {true, 'dapi'};
    optargs(1:numvarargs) = varargin;
    [partialTform, channel] = optargs{:};

    
    %% variables
    numHybCycle = length(hybcycleArray);
    tform = cell(numHybCycle,1);
    imageCheck = cell(numHybCycle,1);
    index = 1;
    
    fprintf('Finding Tform for position %.0f\n', position);
    fileName = ['MMStack_Pos' num2str(position) '.ome.tif'];
    % get the reference
    if isempty(refDir) % if ref dir is empty
        refDir = fullfile(experimentDir, ['HybCycle_' num2str(0)]);
    end
    refPath = getfile(refDir, fileName, 'match');
    [ref,refCh,~,~,~] = grabimseries(refPath, position, channel);
    

    for h = hybcycleArray
        fprintf('HybCycle %.0f...\n', h);
        
        % get moving image
        hybcycleDir = fullfile(experimentDir, ['HybCycle_' num2str(h)]);
        movingPath = getfile(hybcycleDir, fileName, 'match');
        [moving,movingCh,~,~,~] = grabimseries(movingPath, position, channel);
       
        % get the tform
        [tform{index}, imageCheckTemp] = grabtform(moving, ref, partialTform);
        % display tform
        tform{index}.T
        
        % reformat imageChecks
        imageCheck{index} = imageCheckTemp{2};
        imageCheck{index} = imshrink(imageCheck{index});
        index = index + 1;
    end
    



end