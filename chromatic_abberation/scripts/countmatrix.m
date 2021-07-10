function [count, emptyIdx] = countmatrix(geneList, genekey, numCells)
% generates the count matrix from the gene list, key, and number of cells,
% and filters out empty cell
%
% inputs: gene list table, gene key, number of cells
% outputs: count matrix, empty indices
%
% date: 9/22/2020

    % get the count matrix
    count = getcellxgene(geneList, genekey, numCells);
    
    % filter count
    emptyIdx = [];
    for col = size(count,2):-1:2
        if sum(table2array(count(2:end,col))) < 1
            count(:,col) = [];
            emptyIdx = cat(2, emptyIdx, col - 1);
        end
    end

end