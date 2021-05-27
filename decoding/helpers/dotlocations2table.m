function [T, T_unfiltered] = dotlocations2table(dotlocations, barcodekeyNames, minNumSeeds)
% dotlocations2table(dotlocations, barcodekeyNames, minNumSeeds)
%
% description: converts the dotlocations matlab variable to a table format
%
% input: 
% 1. dot locations [cell array]
% 2. barcodekey names [cell array - genes x 1]
% 3. minimum number of seeds [int] - one less than number or rounds
%
% Structure of dot locations per column:
% 1. all consensus points
% 2. channel
% 3. round
% 4. average dot locations across barcode
% 5. intensity
% 6. average intensity
% 7. final dot locations
% 8. number of dot locations colocalized per code
% 9. number of consensus points for each barcode
% 10. number of final points
% 11. number of seeds
% 12. filtered seeds
%
% output: 
% 1. table for each point with x,y,z, intensity, seeds
%
% requirements: 
% - barcodekey names can be extracted from barcodekey.names
%
% notes:
% - number of columns, and the values are different for various versions
%
% date: 11/5/2020

    save('foo.mat', 'dotlocations', 'barcodekeyNames', 'minNumSeeds')
 
    % initialize variables
    x = [];
    y = [];
    z = [];
    seeds = [];
    intensity = [];
    gene = {};
 
    % loop through each row/points and generate variables
    numRows = size(dotlocations,1);
    for r = 1:numRows
        if ~isempty(dotlocations{r,4}) 
            if dotlocations{r,4}(1) ~= 0
                % assign unfiltered dotlocations as x,y,z and intensity/seeds
                numPointsPerRow = size(dotlocations{r,4},1);
                geneRep = cell(numPointsPerRow,1);
                geneRep(:) = {barcodekeyNames{r}};
                gene = cat(1, gene, geneRep);
                x = cat(1, x, dotlocations{r,4}(:,1));
                y = cat(1, y, dotlocations{r,4}(:,2));
                z = cat(1, z, dotlocations{r,4}(:,3));
                intensity = cat(1, intensity, dotlocations{r,6}(:,1));
                seeds = cat(1, seeds, dotlocations{r,11}(:,1));
            end
        end
    end
    
    % unfiltered
    size(gene)
    size(x)
    size(y)
    size(z)
    size(intensity)
    size(seeds)
    
    T_unfiltered = table(gene, x, y, z, intensity);
         
    % filter the table with minimum number of seedes
    T = T_unfiltered %(T_unfiltered.seeds >= minNumSeeds,:);
end
