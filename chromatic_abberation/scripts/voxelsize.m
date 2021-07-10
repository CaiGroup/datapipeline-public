function sizeV = voxelsize(imagePath, position)
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
    if ~isempty(omeMeta.getPixelsPhysicalSizeX(0))
        sizeX = omeMeta.getPixelsPhysicalSizeX(0).value(ome.units.UNITS.MICROMETER).doubleValue();
        sizeY = omeMeta.getPixelsPhysicalSizeY(0).value(ome.units.UNITS.MICROMETER).doubleValue();
    else
        sizeX = [];
        sizeY = [];
    end
    
    
    % assign the voxel size
    if sizeX == sizeY
        sizeV = sizeX;
    elseif ~isempty(sizeX) && isempty(sizeY)
        sizeV = sizeX;
    elseif isempty(sizeX) && ~isempty(sizeY)
        sizeV = sizeY;
    else
        sizeV = [];
        warning 'physical pixel size not found in the metadata of the image';
    end

    
end