function omeXML = omexml(imagePath, position)
% get the size of the voxel in an image
%
% date: 3/31/2020

    % read the image
    r = bfGetReader(imagePath);
    numSeries = r.getSeriesCount();
    if numSeries == 1
        position = 0;
    end
    r.setSeries(position)
    
    
    % get physical pixel size
    omeMeta = r.getMetadataStore();  
    
    % assign the voxel size
    omeXML = char(omeMeta.dumpXML());

    
end



