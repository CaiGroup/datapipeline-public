function [count, cellGlobal, geneGlobal] = savegeneoutput(posArray, outputDataDir, ...
    segDir, saveDir, globalRoiPath, genekey, varargin)
% avegeneoutput(posArray, outputDataDir, segDir, saveDir, globalRoiPath, genekey)
% avegeneoutput(posArray, outputDataDir, segDir, saveDir, globalRoiPath, genekey, localsizeZ, ...
%    localsizeF, localsizeV, maxCellFilter, outputDataStartName, segFileStartName)
% avegeneoutput(posArray, outputDataDir, segDir, saveDir, globalRoiPath, genekey, localsizeZ, ...
%    localsizeF, localsizeV, maxCellFilter, outputDataStartName, segFileStartName, tform)
%
% summary: assign the genelist to global coordinates and save the count matrix and
% the cell locations for all positions
%
% requirments: directory with files only all dotlocations or local genelists
% 1. all directories should only have the dotlocations and/or segmentation
% masks for each position designated by "pos[0-9]", e.g.
% dotlocations_pos9.mat or segmentation_pos9.h5
%
% available to use .csv gene list instead of .mat dotlocations
%
% optional arguments: 
%   localsizeZ - size of z step in um
%   localsizeF - size of fov image width and length in pixels (2048)
%   localsizeV - size of the voxel in local image
%   maxCellFilter - cells removed with area greater than this
%   outputDataStartName - start name of data file if different
%   segFileStartName - start name of labeled segmentation file
%   tform - apply tform to the points if needed (sometimes segmentation
%       image is not aligned to reference image
%
% examples of output and segmentation start names: 
%     for output and seg start names if different than standard:
%     standard - "dotlocations_" "segmentation_"
%     outputDataStartName = 'outputData-SpinalCord-091619-Pos';
%     segFileStartName = 'boundaryseg_MMStack_Pos';
%
% 9/22/2020 


    %% Set up optional Parameters
    argsLimit = 7;
    numvarargs = length(varargin);
    if numvarargs > argsLimit
        error('src:savegeneoutput:TooManyInputs', ...
            'requires at most 7 optional inputs');
    end
    % set defaults for optional inputs
    optargs = {1, 2048, 0.118,  200000, 'dotlocations_', 'segmentation_', []};
    optargs(1:numvarargs) = varargin;
    [localsizeZ, localsizeF, localsizeV, maxCellFilter, outputDataStartName, ...
        segFileStartName, tform] = optargs{:};



    %% Cell locations using RoiSet
    unit = 'both'; % output both units
    % generate local cell coordinate table
    [cellTlocal, L, numCells, noCellIdx] = cellinfo(segDir, segFileStartName, ...
        posArray, maxCellFilter, globalRoiPath, tform);
    % convert to global table
    [cellT, ~] = local2globalcell(cellTlocal, localsizeV, localsizeF, ...
        localsizeZ, globalRoiPath, unit);


    %% assign the points to each local set of cells
    % local coordinates - can insert tform offsets if needed
    genelistpx = assignpoints2cells(segDir, outputDataDir, posArray, ...
        outputDataStartName, segFileStartName, tform);
    % save the table
    saveName = 'genelist_local.csv';
    savePath = fullfile(saveDir, saveName);
    writetable(genelistpx, savePath);


    %% convert local gene list to global coordinate system
    % choose unit
    [geneT, ~] = local2global(genelistpx, localsizeV, localsizeF, ...
        localsizeZ, globalRoiPath, unit, noCellIdx);
    genelistSavePath = fullfile(saveDir, 'genelist_global.csv');
    writetable(geneT, genelistSavePath);


    %% convert the gene list into counts and save
    [count, emptyIdx] = countmatrix(geneT, genekey, numCells);
    % save
    saveCountPath = fullfile(saveDir, 'count_matrix.csv');
    writetable(count, saveCountPath);
    % save for giotto
    saveCountPath = fullfile(saveDir, 'czi_expression.csv');
    writetable(count, saveCountPath);



    %% filter genelist and cells and save the files
    noIdx = setdiff(emptyIdx, noCellIdx);
    geneGlobal = filtergenelist(geneT, noIdx);
    cellfiltT = filtercellinfo(cellT, noIdx);
    % save cell info
    cellGlobal = cellfiltT;
    cellGlobal(:,6:end) = [];
    cellGlobal(:,3) = [];
    % save for Giotto
    cellinfoSavePath = fullfile(saveDir, 'cell_centroids.csv');
    writetable(cellGlobal, cellinfoSavePath);
    cellinfoSavePath = fullfile(saveDir, 'cell_centroids_area.csv');
    writetable(cellfiltT, cellinfoSavePath);
    % save filtered gene list
    saveFiltGenePath = fullfile(saveDir, 'genelist_global.csv');
    writetable(geneGlobal, saveFiltGenePath);
    
    % save the variables
    save(fullfile(saveDir, 'genelist-variables.mat'), 'localsizeZ', 'localsizeF', ...
        'localsizeV', 'maxCellFilter', 'numCells', 'noCellIdx', 'emptyIdx', ...
        'geneT', 'count', 'noIdx', 'geneGlobal', 'cellGlobal');
    
 

end