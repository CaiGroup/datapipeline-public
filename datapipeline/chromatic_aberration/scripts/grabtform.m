function [tform, imageCheck] = grabtform(moving, fixed, varargin)
% grabtform returns the tform between the moving and fixed image.
%
% Inputs: moving image, fixed image, 3d gradient descent optional
% parameters
%
%
% Outputs: tform in 3d
%
% options: partialTform is a boolean to align a 512x512 piece (max int)
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
    % use 200-500 for stringent results for maximum
    % Iterations
    optargs = {false, 0.0063, 100};
    optargs(1:numvarargs) = varargin;
    [partialTform, initRadius, maxIterations] = optargs{:};
  
    
    
    %% Check file existance and call variables
    if ~exist('moving', 'var') && ~exist('fixed', 'var')
        error 'image variables do not exist';
    end
    zSlices = size(moving, 3);
    moving1 = moving;
    fixed1 = fixed;
    

    %% if zslices are less than 16, replicate
    if zSlices < 16
        % replicate z-slices if less than 4
        if zSlices < 16
            mult = ceil(16 / zSlices);
            warning 'Stacking Images with less than 4 zSlices';
            movingRep = repmat(moving1, [1 1 mult]);
            fixedRep = repmat(fixed1, [1 1 mult]);
        end
        % divide image into 4 pieces from 1 image if zslices < 16
        %[moving, ~] = imdivideby4(moving);
        %[fixed, ~] = imdivideby4(fixed);
        
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
    if numvarargs <= (argsLimit - 1)
        initRadius = 0.0625;
    end
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
    
    % if zslice is 1 or less than 4
    if zSlices < 16 || tform.T(4,3) > 4
        % remove the z 
        tform.T(4,3) = 0;
    end
    imref = imref3d(size(moving1));
    
    
    %% return cell array of the image
    imageCheck = cell(1,2);
    imageCheck{1} = fixed1;
    movingAligned = imwarp(moving1, tform, 'OutputView', imref);
    imageCheck{2} = movingAligned;
    
    
end