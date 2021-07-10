function [points, numpointspercell] = orgcell2points(spotslocation, spotsintensity, spotsintensityscaled, numRounds, numPseudoChannels, zSlice)
% function to reorganize points to structure originally used in
% barcodeNoMijiv8
%
% Input: spotslocation - a hybs x 1 cell array
%
% Date: 8/15/2019

    if isempty(spotsintensityscaled)
        spotsintensityscaled = cellfun(@(x) x(:) / mean(x(:)), spotsintensity, 'UniformOutput', false);
    end
    
    points = cell(1, numRounds);
    numpointspercell = 0;
    for r = 1:numRounds
        points{r} = struct('channels', cell(1, numPseudoChannels));
        points{r} = struct('intensity', cell(1, numPseudoChannels));
        points{r} = struct('scaledIntensity', cell(1, numPseudoChannels));
        for c = 1:numPseudoChannels
            hybIndex = (r-1) * numPseudoChannels + c;
            points{r}(c).channels = spotslocation{hybIndex};
            if ~isempty(zSlice)
                points{r}(c).channels(:,3) = zSlice;
            end
            points{r}(c).intensity = spotsintensity{hybIndex};
            points{r}(c).scaledIntensity = spotsintensityscaled{hybIndex};
            numpointspercell = numpointspercell + size(spotslocation{hybIndex},1);
        end
    end




end

