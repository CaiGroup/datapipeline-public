function I = applyalltform(im, tform)
% apply all dapi tforms to the cell array of images
%
% date: 2/22/20

    numIm = size(im,1);
    numCh = size(im,2);
    I = cell(numIm, numCh);
    for i = 1:numIm
            I(i,:) = applydapitform(im(i,:), tform{i});
    end

end