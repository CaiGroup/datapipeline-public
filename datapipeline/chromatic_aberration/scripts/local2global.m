function [T, Tfov] = local2global(T, localsizeV, localsizeF, ...
    localsizeZ, globalRoiPath, varargin)
% converts local table T from local/pixels to global/microns
%
% option to convert from local to global pixels, set
% >> unit = 'px';
% >> T, Tfov] = local2global(T, localsizeV, localsizeF, ...
%    globalRoiPath, localsizeZ, unit);
%
% filterIdx used to filter out any points not in filter cells
%
% T is the gene list in pixels, localsizeV is the local voxel size (should
% be around 0.11), localsizeF is the local fov size and globalsizeF is for
% global, and localsizeZ is the zStep for z-slices in microns.
%
% 3/31/2020



    %% Set up optional Parameters
    argsLimit = 2;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('seqfish:local2globalcell:TooManyInputs', ...
            'requires at most 3 optional inputs');
    end
    % set defaults for optional inputs
    optargs = {'um',[]};
    optargs(1:numvarargs) = varargin;
    [unit, noCellIdx] = optargs{:};
    
    

    %% variables
    globalsizeF = fovsize(globalRoiPath);
    global2local = localsizeF / globalsizeF;
    if strcmp(unit, 'px')
        localsizeV = 1;
        localsizeZ = 1;
    end
    
    %% get the coordinates for the global ROIs
    fov = [];
    y = [];
    x = [];
    vertex = selfsegzip(globalRoiPath);
    for i = 1:length(vertex)
        % get top left corner
        fov = cat(1, fov, i);
        x = cat(1,x,vertex(i).x(1));
        y = cat(1,y,vertex(i).y(1));
        % add this top left corner to the x,y coordinates then multiply the
        % global voxel size variable
    end
    min_x = min(x);
    min_y = min(y);
    x = (x - min_x) .* global2local;
    y = (y - min_y) .* global2local;
    Tfov = table(fov, x, y);
    
    
    %% filter out points with the cell indices
    T = filtergenelist(T, noCellIdx);

    
    %% get the table 
    if strcmp('px', unit) || strcmp('um', unit)
        for i = 0:max(T.fieldID)
            idx = find(T.fieldID == i);
            T.x(idx) = (T.x(idx) + x(i+1)) .* localsizeV;
            T.y(idx) = (T.y(idx) + y(i+1)) .* localsizeV;
            T.z(idx) = T.z(idx);
        end
    elseif strcmp('both', unit)
        for i = 0:max(T.fieldID)
            idx = find(T.fieldID == i);
            % pixels
            T.x_px(idx) = (T.x(idx) + x(i+1));
            T.y_px(idx) = (T.y(idx) + y(i+1));
            T.z_px(idx) = T.z(idx);
            % um
            T.x(idx) = (T.x(idx) + x(i+1)) .* localsizeV;
            T.y(idx) = (T.y(idx) + y(i+1)) .* localsizeV;
            T.z(idx) = T.z(idx) .* localsizeZ;
        end
    end

end