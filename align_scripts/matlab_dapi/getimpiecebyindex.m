function [I] = getimpiecebyindex(image, index, varargin)
% function to divide the image into 8 pieces use the image with the highest
% average of pixels
%
% default division factor is 8
%
% Date 3/11/2019

    %% Set up optional Parameters for z-slice index
    argsLimit = 1;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('myfun:impiecemaxint:TooManyInputs', ...
            'requires at most 1 optional inputs');
    end
    % Error for type of arguments
    if numvarargs >= 1 
        if ~isnumeric(varargin{1})
            error('myfun:impiecemaxint:WrongInput', ...
                'initRadius requires type double');  
        end
    end
    optargs = {8};
    optargs(1:numvarargs) = varargin;
    [divFactor] = optargs{:};
    
    %% Main Function
    bound = divFactor/2;
    pixelDiv = fix(size(image,1) / bound); % for each axis
    
    % get the pieces of the image
    im = cell(divFactor,1);
    imavg = ones(divFactor,1);
    idx = 1;
    for c = 1:bound
        for r = 1:bound
            colstart = (c-1) * pixelDiv + 1;
            rowstart = (r-1) * pixelDiv + 1;
            colend = colstart + pixelDiv - 1;
            rowend = rowstart + pixelDiv - 1;
            col = colstart:colend;
            row = rowstart:rowend;
            im{idx} = image(col,row,:);
            imavg(idx) = median(im{idx},'all');
            idx = idx + 1;
        end
    end


    % use the image index for alignment
    I = im{index};
    
end