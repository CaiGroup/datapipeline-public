function I = applydapitform(image, tform)    
% applys tform to image in cell array
%
% Return image with applied transformation
%
% Author: Nico Pierson
% Email: nicogpt@caltech.edu
% Date: 2/26/2019

    % Variables
    numDim = length(tform.T);
    if numDim ~= 3 && numDim ~= 4
        error 'tform does not have the right number of dimensions';
    end
    if iscell(image)
        numChannels = length(image);
        I = cell(1, numChannels);
    else
        numChannels = 1;
    end
    
    

    if numDim == 4
        for i = 1:numChannels
            if iscell(image)
                I{i} = imwarp(image{i}, tform, 'OutputView', imref3d(size(image{i})));
            else
                I = imwarp(image, tform, 'OutputView', imref3d(size(image)));
            end
        end
    elseif numDim == 3
        numZ = size(image{1},3);
        for i = 1:numChannels
            for z = 1:numZ
                if iscell(image)
                    I{i}(:,:,z) = imwarp(image{i}(:,:,z), tform, 'OutputView', imref2d(size(image{i}(:,:,z))));
                else
                    I(:,:,z) = imwarp(image(:,:,z), tform, 'OutputView', imref2d(size(image(:,:,z))));
                end
            end
        end
    end
    
    
end