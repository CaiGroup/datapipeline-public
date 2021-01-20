function tform = grabcelltform(I, refI, varargin)
% gets all the tforms for cell array and returns tform of cell arrays
%
% date: 2/22/20


    %% Set up optional Parameters for z-slice index
    argsLimit = 3;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('myfun:grabtform:TooManyInputs', ...
            'requires at most 3 optional inputs');
    end
    % Error for type of arguments
    if numvarargs >= 2
        if ~isnumeric(varargin{1})
            error('myfun:grabtform:WrongInput', ...
                'initRadius requires type double');  
        end
    end
    if numvarargs >= 3
        if ~isnumeric(varargin{2}) || ~isscalar(varargin{2})
            error('myfun:grabtform:WrongInput', ...
                'numIterations requires type int');  
        end
    end
    % use 200-500 for stringent results for maximum
    % Iterations
    optargs = {false, 0.0063, 100};
    optargs(1:numvarargs) = varargin;
    [partialTform, initRadius, maxIterations] = optargs{:};
    
    
    %% get the tform for each image
    
    if iscell(I)
        numIm = length(refI);
        tform = cell(numIm, 1);
    else
        numIm = 1;
    end
    for i = 1:numIm
        if iscell(I)
            tform{i} = grabtform(I{i}, refI{i}, partialTform, initRadius, maxIterations);
        else
             tform = grabtform(I, refI, partialTform, initRadius, maxIterations);
        end
    end

end