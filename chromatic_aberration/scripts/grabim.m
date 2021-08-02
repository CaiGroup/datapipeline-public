function [I, sizeC] = grabim(dir, position, varargin)
% get the image from the directory and position, assuming the filename is
% MMStack_Pos[1-9].ome.tif
%
% optional parameter: format of string with the %d for the position number

    %% Set up optional Parameters
    numvarargs = length(varargin);
    argsLimit = 2;
    if numvarargs > argsLimit
        error('myfuns:getim:TooManyInputs', ...
            'requires at most 2 optional inputs');
    end
    % set defaults for optional inputs
    optargs = {[], 'MMStack_Pos%d.ome.tif'}; 
    optargs(1:numvarargs) = varargin;
    % Place optional args in memorable variable names
    [channel, imName] = optargs{:};
    
    
    
    %% get the image
    imName = sprintf(imName, position);
    imPath = getfile(dir, imName, 'match');
    if isempty(imPath)
        error 'file not found';
    end
    [I, sizeC, sizeZ, physicalsizeX, physicalsizeY] = grabimseries(imPath, ...
        position, channel);

end