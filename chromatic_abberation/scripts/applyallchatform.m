function I = applyallchatform(im, tform)
% apply all chromatic aberration tforms to the cell array of images
%
% date: 2/22/20

    numIm = size(im,1);
    numCh = size(im,2);
    I = cell(numIm, numCh);
    for i = 1:numIm
        for ch = 1:numCh
            I{i,ch} = imwarp(im{i,ch}, tform{ch}, 'OutputView', imref3d(size(im{i,ch})));
        end
    end

end