function [] = printallimagespos(I, saveDir, startString, endingString)
% prints all the images using 5 of the middle zslices
%
% dependencies: Fiji, with the ij.jar and mij.jar in the javaclasspath of
% MATLAB
%
% date: 3/2/2020


    % varables
    numPosRow = size(I,1);
    numPosCol = size(I,2);
    if numPosRow >= numPosCol
        numPos = numPosRow;
    else
        numPos = numPosCol;
    end
    
    % get the correct z slice
    sizeZ = size(I{1},3);
    numZSlices = 5;
    if sizeZ > numZSlices
        half = round(sizeZ / 2);
        z1 = half - 2;
        z2 = half + 2;
    end
        
    
    image = I;
    for position = 1:numPos
        image{position} = I{position}(:,:,z1:z2);
    end
    savecellbypos(image, saveDir, startString, endingString);

end