function [tform, imageCheck] = tformallpos(movingDir, fixedDir, posArray, varargin)
% wrapper function to get all the tforms between the last channels of the
% image
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
    optargs = {false, 'dapi'};
    optargs(1:numvarargs) = varargin;
    [partialTform, channel] = optargs{:};

    
    %% variables
    numPos = length(posArray);
    tform = cell(numPos,1);
    imageCheck = cell(numPos,1);
    index = 1;
    
    for position = posArray
        fprintf('Finding Tform for position %.0f\n', position);
        fileName = ['MMStack_Pos' num2str(position) '.ome.tif'];
        % get moving image
        movingPath = getfile(movingDir, fileName, 'match');
        [moving,movingCh,~,~,~] = grabimseries(movingPath, position, channel);
        % get fixed image
        fixedPath = getfile(fixedDir, fileName, 'match');
        [fixed,fixedCh,~,~,~] = grabimseries(fixedPath, position, channel);
        % get the tform
        [tform{index}, imageCheck{index}] = grabtform(moving, fixed, partialTform);
        index = index + 1;
    end



end