function [img, sizeC, sizeZ, physicalsizeX, physicalsizeY] = loadometiff(imagePath, position, varargin)
% loadometiff(imagePath, position)
% loadometiff(imagePath, position, channel)
% loadometiff(imagePath, position, channel, numChannels)
%
% loads OME.TIFF images for every channel, or a selected channel, and
% outputs in (z, c, x, y)
% 
% inputs:
% 1. image path [string]
% 2. position [int]
% 3. (optional) channel selector [int] or 'dapi' [string]
% 4. (optional) number of channels [int] - sometimes TIFF images are
% improperly formatted; this will organize the image based on number of
% channels
% 
% outputs:
% 1. img - 4D image (z,c,x,y) [n-array]
% 2. number of channels [int]
% 3. number of z-slices [int]
% 4. physical size x [float] in metadata
% 5. physical size y [float] in metadata
%
% Dependencies:
% 1. bfmatlab folder needs to be in MATLAB path
% example: addpath('C:\Users\Long Cai - 2\Desktop\Fiji.app\scripts\', '-end');
% 2. bio-formats.jar to java class path in matlab
% example: javaaddpath('C:\Users\Long Cai - 2\Box\code\io\bfmatlab\bioformats_package.jar');
%
% optional arg: channel gives the image of a specific channel, or use
% 'dapi' to get last channel
%
% Code adapted from bfmatlab package
% Date: 5/7/2019

%% Set up optional Parameters
    argsLimit = 2;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('src:grabimseries:TooManyInputs', ...
            'requires at most 2 optional inputs');
    end
    % set defaults for optional inputs
    optargs = {[], 1};
    % assign defaults
    optargs(1:numvarargs) = varargin;
    % Default Value of ref image is 1
    [channel, numC] = optargs{:};
    
    dimensionOrder = [];
    sizeC = [];
    sizeZ = [];
    sizeT = [];
    r = bfGetReader(imagePath);
    numSeries = r.getSeriesCount();
    if numSeries == 1
        position = 0;
        s=1; % series
    else
        s = position+1;
    end
    r.setSeries(position)
    pixelType = r.getPixelType();
    bpp = javaMethod('getBytesPerPixel', 'loci.formats.FormatTools', ...
    pixelType);
    bppMax = power(2, bpp * 8);
    numImages = r.getImageCount();
    imageList = cell(numImages, 2);
    colorMaps = cell(numImages);
    id = imagePath;
    globalMetadata = r.getGlobalMetadata();
    for i = 1:numImages
        %{ 
        take out print statements
        %if mod(i, 72) == 1
            %fprintf('\n    ');
        %end
        %fprintf('.');
        %}
        arr = bfGetPlane(r, i);
        % retrieve color map data
        if bpp == 1
            colorMaps{s, i} = r.get8BitLookupTable()';
        else
            colorMaps{s, i} = r.get16BitLookupTable()';
        end
        warning_state = warning ('off');
        if ~isempty(colorMaps{s, i})
            newMap = single(colorMaps{s, i});
            newMap(newMap < 0) = newMap(newMap < 0) + bppMax;
            colorMaps{s, i} = newMap / (bppMax - 1);
        end
        warning (warning_state);
        % build an informative title for our figure
        label = id;
        if numSeries > 1
            seriesName = char(r.getMetadataStore().getImageName(s - 1));
            if ~isempty(seriesName)
                label = [label, '; ', seriesName];
            else
                qs = int2str(s);
                label = [label, '; series ', qs, '/', int2str(numSeries)];
            end
        end
        if numImages > 1
            qi = int2str(i);
            label = [label, '; plane ', qi, '/', int2str(numImages)];
            if r.isOrderCertain()
                lz = 'Z';
                lc = 'C';
                lt = 'T';
            else
                lz = 'Z?';
                lc = 'C?';
                lt = 'T?';
            end
            zct = r.getZCTCoords(i - 1);
            
            sizeZ = r.getSizeZ();
            if sizeZ > 1
                qz = int2str(zct(1) + 1);
                label = [label, '; ', lz, '=', qz, '/', int2str(sizeZ)];
            else
                sizeZ = numImages / numC;
                if sizeZ > 1 
                    qz = int2str(zct(1) + 1);
                    label = [label, '; ', lz, '=', qz, '/', int2str(sizeZ)];
                end
            end
            
            sizeC = r.getSizeC();
            if sizeC > 1
                qc = int2str(zct(2) + 1);
                label = [label, '; ', lc, '=', qc, '/', int2str(sizeC)];
            else
                sizeC = numImages / sizeZ;
                dimensionOrder = 'XYZCT';
                if sizeC > 1
                    qc = int2str(zct(2) + 1);
                    label = [label, '; ', lc, '=', qc, '/', int2str(sizeC)];
                end
            end
            
            
            sizeT = r.getSizeT();
            if sizeT > 1
                qt = int2str(zct(3) + 1);
                label = [label, '; ', lt, '=', qt, '/', int2str(sizeT)];
            end
        else
            sizeC = 1;
            sizeZ = 1;
            sizeT = 1;
        end
        
        % save image plane and label into the list
        imageList{i, 1} = arr;
        imageList{i, 2} = label;
    end

    % per position
    s = 1;
    result{s, 1} = imageList;
    % extract metadata table for this series
    seriesMetadata = r.getSeriesMetadata();
    javaMethod('merge', 'loci.formats.MetadataTools', ...
    globalMetadata, seriesMetadata, 'Global ');
    if isempty(dimensionOrder)
        dimensionOrder = r.getDimensionOrder();
    end
    result{s, 2} = seriesMetadata;
    result{s, 3} = colorMaps;
    result{s, 4} = r.getMetadataStore();
    
    % get physical pixel size
    omeMeta = r.getMetadataStore();
    if ~isempty(omeMeta.getPixelsPhysicalSizeX(0))
        physicalsizeX = omeMeta.getPixelsPhysicalSizeX(0).value(ome.units.UNITS.MICROMETER).doubleValue();
        physicalsizeY = omeMeta.getPixelsPhysicalSizeY(0).value(ome.units.UNITS.MICROMETER).doubleValue();
    else
        physicalsizeX = [];
        physicalsizeY = [];
    end


    if ischar(channel)
        if strcmp(channel, 'dapi')
            % get last channel
            chArray = sizeC;
        end
    elseif ~isempty(channel)
        chArray = channel;
    else
        chArray = 1:sizeC;
    end
    
    % get channels per image
    chIndex = 1;
    for ch = chArray
        A = getchim(dimensionOrder, ch, sizeC, sizeZ, numImages, result);
        % permute (y, x, z) to (z, x, y)
        img(:,chIndex,:,:) = permute(A{1},[3 2 1]);
        chIndex = chIndex + 1;
    end
    
end