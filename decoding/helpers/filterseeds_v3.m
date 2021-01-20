function [finalPosList, PosList, dotlocationsfinal, matNumDotLocations, matNumPointConsensus, ...
    matNumFinalPoints] = filterseeds_v3(seedlist, dotlocations, minnumseeds, varargin)
% filterseeds returns the final position list by using a threshold of the
% required number of seeds. 
%
% input: 
% 1. seeds [cell array] from numseeds.m
% 2. dot locations [cell array - genes x 1] from PointLocations.m
% 3. minimum number of seeds [int] - one less than number or rounds
%
% Outputs: 
% 1. finalPosList [cell array] gene by cell with dot locations filtered by
% seeds.
% 2. PosList [cell array] gene by cell array with no filtering
% 3. dotlocationsfinal [cell array] updated dotlocations with description
% below.
% 4. matNumDotLocations [cell array] bug returning something else
% 5. matNumPointConsensus [cell array] gene by cell - number of
% 6. matNumFinalPoints [cell array] gene by cell - number of filtered points
%
% Update: 2/22/2019
% - Took out updating finalPos for 'whole' (all cells) or 'roi' (each cell),
% because the finalPosList outputs only one coloumn for the 'whole' option
% and all the cells for the 'roi' option
%
% Organization of dotlocations by column
% 1. all consensus points
% 2. channel
% 3. round
% 4. average location of points across barcode
% 5. intensity
% 6. average intensity
% 7. final dot locations
% 8. number of dot locations colocalized per code
% 9. number of consensus points for each barcode
% 10. number of final points
% 11. number of seeds
% 12. filtered seeds
% 
% Author: Mike Lawson
% Date: 2018
% Edited By: Nico Pierson
% Updated: August 5, 2019

    %% Set up optional Parameters for z-slice index
    % Either the final position list will add all the ROI points together
    % 'all cells' or each cell will keep the positions 'each cell'
    numvarargs = length(varargin);
    if numvarargs > 1
        error('myfun:filterseeds:TooManyInputs', ...
            'requires at most 1 optional inputs');
    end

    % Error for type of arguments
    if numvarargs >= 1 
        if ~ischar(varargin{1}) 
            error('myfun:filterseeds:WrongInput', ...
                'call barcodes requires type string');
        elseif ~strcmp(varargin{1}, 'roi') && ~strcmp(varargin{1}, 'whole') 
            error('myfun:filterseeds:WrongInput', ...
                'call barcodes requires type string: "roi" or "whole"');
        end
    end

    % set defaults for optional inputs
    optargs = {'roi'}; % 'roi' for each cells individually or 'whole' for processing whole field

    % now put these defaults into the valuesToUse cell array, 
    % and overwrite the ones specified in varargin.
    optargs(1:numvarargs) = varargin;

    % Default Value of ref image is 1
    [cellTogether] = optargs{:};

    %% Filter the seeds
    % number of seeds is the amount of seeds needed to be considered a
    % point, ex. for 4 barcode rounds, numseeds = 3. Usually barcode - 1. %
    % Can't have uniform output....or else turns b into logical matrix?
    %cleanseedlist = cleanfilterseeds(seedlist, 6); % Set to 6 for now... Fix getting the seeds for gene 2-Mar on row 7666
    %b = cellfun(@(x) x >= numseeds,seedlist(:,1), 'UniformOutput',0);
    b = cellfun(@(x) x >= minnumseeds,seedlist(:,1),'UniformOutput',0); % Creates logical indices of which cells satisfy the conditional
    %b = cellfun(@(b) size(b, 2) < 2, b); HOW TO TAKE OUT NON SCALARS??
    matfinalpointssum = cellfun(@sum,b);
    dotlocationsfinal = dotlocations;
    
    for i = 1:size(b,1) % for x length of cells
       if ~isempty(b{i})
           dotlocationsfinal{i, 7} = dotlocationsfinal{i, 4}; % new column for filtered points
           dotlocationsfinal{i, 7}(~b{i},:) = []; % set all seeds less than numseeds to null
           
           % set column 7 equal to the number of dot locations colocalized
           % per barcode
           dotlocationsfinal{i, 8} = size(dotlocationsfinal{i, 1}, 1);
           % set column8 to the number of consensus points for each barcode
           dotlocationsfinal{i, 9} = size(dotlocationsfinal{i, 4}, 1);
           % set column 9 to number of final points
           dotlocationsfinal{i, 10} = size(dotlocationsfinal{i, 6}, 1);
           % column 10 are all the seeds
           dotlocationsfinal{i, 11} = seedlist{i};
           % set column 10 for final points seeds
           dotlocationsfinal{i, 12} = seedlist{i};
           dotlocationsfinal{i,12}(~b{i},:) = [];

       end
    end
    if ~isempty(dotlocationsfinal)
        finalPosList = dotlocationsfinal(:,6);
        PosList = dotlocationsfinal(:,1);
        matNumDotLocations = dotlocationsfinal(:,7);
        matNumPointConsensus = dotlocationsfinal(:,8);
        matNumFinalPoints = dotlocationsfinal(:,9);
    else
        finalPosList = [];
        PosList = [];
        matNumDotLocations = [];
        matNumPointConsensus = [];
        matNumFinalPoints = [];
    end
    
end