function sizeP = fovsize(roipath)
% script to get size of the global tiles in pixels
%
% date: 3/31/2020

    % variables
    vertex = selfsegzip(roipath);
    sizeY = [];
    sizeX = [];
    
    % iterate over each fov ROI
    for i = 1:length(vertex)
        bound_xTemp = vertex(i).x;
        bound_yTemp = vertex(i).y;
        sizeY = cat(2, sizeY, abs(bound_yTemp(1) - bound_yTemp(2)));
        sizeX = cat(2, sizeX, abs(bound_xTemp(2) - bound_xTemp(3)));
    end
    
    % get the average
    avgY = mean(sizeY);
    avgX = mean(sizeX);
    
    % assign to sizeP
    if avgY == avgX
        sizeP = avgY;
    else
        sizeP = (avgY + avgX) / 2;
    end
   
end
