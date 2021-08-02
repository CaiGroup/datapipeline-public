function [cellxgene, numcellxgene] = cellgenesavewrapper(T, posArray, saveDir, barcodeDir, numCells)
% wrapper function to save the cell by gene and count matrices to csv in
% the experiment
%
% T is the table from the assignpoints2cell.m
%
% saveDir is usually saved in the 'experiment\analysis' directory
%
% barcodeDir will have the barcodekey
%
% date: 3/11/2020

    %% gene by cell table
    barcodeGenePath = getfile(barcodeDir, '.', 'match');
    geneT = readtable(barcodeGenePath);
    cellxgene = cell(length(posArray),1);
    numcellxgene = cell(length(posArray),1);
    

    cgsaveDir = fullfile(saveDir, 'cell-gene-matrix');
    ncgsaveDir = fullfile(saveDir, 'count-matrix');
    mkdir(cgsaveDir);
    mkdir(ncgsaveDir);
    
    % for each position save the cell gene and count matrix
    iter = 1;
    for fov = posArray
        fprintf('cell gene matrix for position %.0f\n', fov);
        numCell = numCells(fov+1);
        [cellxgene{iter}, numcellxgene{iter}] = makecellxgene(T, geneT, fov, numCell);
        cgSaveName = ['cell-gene-matrix-pos' num2str(fov) '.csv'];
        ncgSaveName = ['count-matrix-pos' num2str(fov) '.csv'];
        cgSavePath = fullfile(cgsaveDir, cgSaveName);
        ncgSavePath = fullfile(ncgsaveDir, ncgSaveName);
        writetable(cellxgene{iter}, cgSavePath);
        writetable(numcellxgene{iter}, ncgSavePath);
        iter = iter + 1;
    end


end