function [tform, imageCheck] = grabtform(moving, fixed, varargin)
% grabtform(moving, fixed);
% grabtform(moving, fixed, partialTform);
% grabtform(moving, fixed, partialTform, initRadius);
% grabtform(moving, fixed, partialTform, initRadius, maxIterations);
% 
% description: returns forward spatial transformation for aliging moving to
% fixed image. QC image is returned as well.
%
% input: 
% 1. moving image [uint32]
% 2. fixed image [uint32]
% 3. (optional) partial tform [boolean] - (default) false, uses part of
% image for transformation which speeds up algorithm.
% 4. (optional) initRadius [double]: 0.0625 (default), initial ball radius for
% gradient descent in imregtform.m
% 5. (optional) maxIterations [int]: 100 (default), number of max
% iterations of gradient descent in imregtform.m
%
% output: tform [affine 3d object], image of aligned moving and fixed [cell
% array][uint32]
%
% note:
% - tform in z is set to 0 for images with z-slices < 16 and if the offset
% is more than 4
%
% Author: Nico Pierson
% Email: nicogpt@caltech.edu
% Date: 2/26/2019
% Modified: 3/10/2020


    %% Set up optional Parameters for z-slice index
    argsLimit = 3;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('myfun:grabtform:TooManyInputs', ...
            'requires at most 3 optional inputs');
    end
    % Error for type of arguments
    if numvarargs > 1
        if ~isnumeric(varargin{2})
            error('myfun:grabtform:WrongInput', ...
                'initRadius requires type double');  
        end
    end
    if numvarargs > 2
        if ~isnumeric(varargin{3}) || ~isscalar(varargin{3})
            error('myfun:grabtform:WrongInput', ...
                'numIterations requires type int');  
        end
    end
    % set up optional args
    optargs = {false, 0.0625, 100};
    optargs(1:numvarargs) = varargin;
    [partialTform, initRadius, maxIterations] = optargs{:};
  
    
    %% Check file existance and call variables
    if ~exist('moving', 'var') && ~exist('fixed', 'var')
        error 'image variables do not exist';
    end
   
    
    %% initial variables
    zSlices = size(moving, 3);
    moving1 = moving;
    fixed1 = fixed;
    

    %% if zslices are less than 16, replicate 
    % gradient descent for imregtform only works on more than 15 z
    if zSlices < 16
        % replicate z-slices if less than 4
        if zSlices < 16
            mult = ceil(16 / zSlices);
            warning 'Stacking Images with less than 4 zSlices';
            movingRep = repmat(moving1, [1 1 mult]);
            fixedRep = repmat(fixed1, [1 1 mult]);
        end
        
        % get the piece with the largest intensity
        [fixed, index1] = impiecemaxint(fixedRep);
        [moving, index2] = impiecemaxint(movingRep);
        if index1 ~= index2
            warning('impiecemaxint.m has mismatching indices');
            % use index1
            moving = getimpiecebyindex(movingRep, index1);
        end
        partialTform = false;
    end
    
    %% align 512x512 piece
    if partialTform
        % get the piece with the largest intensity
        [fixed, index1] = impiecemaxint(fixed1);
        [moving, index2] = impiecemaxint(moving1);
    end
    
    
    %% 3d gradient descent
    [optimizer, metric] = imregconfig('monomodal'); % use monomodal for 3d tforms
    optimizer.MaximumStepLength = initRadius; % 0.0625 is the default for the regular step gradient descent
    optimizer.MaximumIterations = maxIterations;
    warning(''); % clear warnings
    tform = imregtform(moving, fixed, 'translation', optimizer, metric);

    % get any warning messages
    [warnMsg, warnId] = lastwarn;
    if ~isempty(warnMsg) % do something if there is a warning
        fprintf('Rerunning imregtform on whole image\n');
        if zSlices < 16
             tform = imregtform(movingRep, fixedRep, 'translation', optimizer, metric);
        else
             tform = imregtform(moving1, fixed1, 'translation', optimizer, metric);
        end
    end
    
    % set to 0 if zslice is 16 or if shift in z is > 4
    if zSlices < 16 || tform.T(4,3) > 4
        % remove the z 
        tform.T(4,3) = 0;
    end
    if size(moving1,3) > 1
        imref = imref3d(size(moving1));
    else
        imref = imref2d(size(moving1));
        tformTemp = tform;
        tform = affine2d(eye(3));
        tform.T(3,1) = tformTemp.T(4,1);
        tform.T(3,2) = tformTemp.T(4,2);
    end
    
    
    %% return cell array of the image
    % first cell image is fixed
    % second cell is the aligned moving image
    imageCheck = cell(1,2);
    imageCheck{1} = fixed1;
    movingAligned = imwarp(moving1, tform, 'OutputView', imref);
    imageCheck{2} = movingAligned;
    
    
end