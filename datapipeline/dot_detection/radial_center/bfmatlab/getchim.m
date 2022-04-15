function I = getchim(dimensionOrder, chArray, sizeC, sizeZ, numImages, result)
% getchim(dimensionOrder, chArray, sizeC, sizeZ, numImages, result)
%
% gets the image from the specific channel from the cell array in result of
% loadometiff.m
%
% inputs:
% 1. dimension order [string]
% 2. channel array [array or int]
% 3. number of channels [int]
% 4. number of z-slices [int]
% 5. image result [cell array]
%
% outputs:
% 1. I [cell array] - selected image
% 
% date: 2019

    %% variables
    I = cell(1, length(chArray));
    
    
    %% get the image from result
    index = 1;
    for i = chArray
        if strcmp(dimensionOrder, 'XYCZT')
            indices = i:sizeC:numImages;
        elseif strcmp(dimensionOrder, 'XYZCT')
            startIndex = sizeZ * (i - 1) + 1;
            endIndex = startIndex + sizeZ - 1;
            indices = startIndex:endIndex;
        end
        for j = indices
            I{index} = cat(3,I{index}, result{1,1}{j,1});
        end
        index = index + 1;
    end

end