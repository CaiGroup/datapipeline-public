function [T, Tfov] = local2globalcell(cellT, localsizeV, localsizeF, ...
    localsizeZ, globalRoiPath, varargin)
% converts local table T from local/pixels to global/microns
%
% option to convert from local to global pixels, set
% >> unit = 'px';
% >> T, Tfov] = local2globalcell(T, localsizeV, localsizeF, ...
%    localsizeZ, globalRoiPath, unit);
%
% cellT is the cell info table in pixels, localsizeV is the local voxel size (should
% be around 0.11), localsizeF is the local fov size and globalsizeF is for
% global, and localsizeZ is the zStep for z-slices in microns.
%
% 3/31/2020


    %% Set up optional Parameters
    argsLimit = 1;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('seqfish:local2globalcell:TooManyInputs', ...
            'requires at most 1 optional inputs');
    end
    % set defaults for optional inputs
    optargs = {'um'};
    optargs(1:numvarargs) = varargin;
    [unit] = optargs{:};
 


    % variables
    if ismember('Volume', cellT.Properties.VariableNames)
        dim = '3d';
    else
        dim = '2d';
    end
    % variables
    globalsizeF = fovsize(globalRoiPath);
    global2local = localsizeF / globalsizeF;
    if strcmp(unit, 'px')
        localsizeV = 1; % remove the voxel size converter
    end
    
    
    % get the coordinates for the global ROIs
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

    Tfov = table(fov, x, y);
    
    
    T = cellT(:,1:2);
    if strcmp('px', unit) || strcmp('um', unit)
        for i = 0:max(cellT.FieldID)
            idx = find(cellT.FieldID == i);
            T.x(idx) = cellT.X(idx) .* localsizeV;
            T.y(idx) = cellT.Y(idx) .* localsizeV;
            if strcmp(dim, '3d')
                T.z(idx) = cellT.Z(idx) .* localsizeZ;
                T.size = cellT.Volume .* localsizeV;
            end
        end
    elseif strcmp('both', unit)
        for i = 0:max(cellT.FieldID)
            idx = find(cellT.FieldID == i);
            % pixels
            T.x_px(idx) = cellT.X(idx);
            T.y_px(idx) = cellT.Y(idx);
            % um
            T.x_um(idx) = cellT.X(idx) .* localsizeV;
            T.y_um(idx) = cellT.Y(idx) .* localsizeV;
            if strcmp(dim, '3d')
                T.size_px = cellT.Volume;
                T.size_um = cellT.Volume .* localsizeV;
                T.z_px(idx) = cellT.Z(idx);
                T.z_um(idx) = cellT.Z(idx) .* localsizeZ;
            else
                T.size_px = cellT.Area;
                T.size_um = cellT.Area .* localsizeV;
            end
            
        end
    end

end