function [ pts1, pts2, called1, called2, pair ] = colocalizedots(image1, image2, dots1, dots2, radius, debug)
% function colocalizes dots and returns the unique set of points within a
% specifid radius
%
% Output: pts1 and pts2 are organized as [y x z]
% - Does this need to be fixed for the colocalize graph?
%
% Things To Do:
% 1. Comment and Clean the Code
%
% Author: Sheel Shah
% Date: March 2018
% Modified By: Nico Pierson
% Email: nicogpt@caltech.edu
% Date: 1/29/2019


    % idx gives the indice of the closest point for each of points2
    % D gives the distance for idx
    % idx2 gives the indice of the closest point for each of points1
    % D gives the distance for idx2

    % find all points within the range of the radius for image1 and image2 dots
    [idx,D]= rangesearch(dots1,dots2,radius+.00001);
    [idx2,D2] = rangesearch(dots2,dots1,radius+.00001);
    pair = [];
    if ~isempty(idx) && ~isempty(idx2)
        %Match Unique Points symmetrically
        idx2temp = idx2;
        D2temp = D2;
        for i = 1:length(idx)
            if length(idx{i}) == 1
                if length(idx2{idx{i}}) == 1
                    idxtemp{i,1} = idx{i};
                    Dtemp{i,1} = D{i};
                else
                    dummy = idx2{idx{i}};
                    dummyD = D2{idx{i}};
                    matches = cellfun(@length,idx(dummy))';
                    keepers = matches == 1;
                    idxtemp{i,1} = idx{i};
                    Dtemp{i,1} = D{i};
                    idx2temp{idx{i}} = dummy(keepers);
                    D2temp{idx{i}} = dummyD(keepers);
                end
            else
                idxtemp{i,1} = idx{i};
                Dtemp{i,1} = D{i};
            end
        end

        idxunique = idxtemp;
        Dunique = Dtemp;
        for i = 1:length(idx2temp)
            if length(idx2temp{i}) == 1
                if length(idxtemp{idx2temp{i}}) == 1
                    idx2unique{i,1} = idx2temp{i};
                    D2unique{i,1} = D2temp{i};
                else
                    dummy = idxtemp{idx2temp{i}};
                    dummyD = Dtemp{idx2temp{i}};
                    matches = cellfun(@length,idx2temp(dummy))';
                    keepers = matches == 1;
                    idx2unique{i,1} = idx2temp{i};
                    D2unique{i,1} = D2temp{i};
                    idxunique{idx2temp{i}} = dummy(keepers);
                    Dunique{idx2temp{i}} = dummyD(keepers);
                end
            else
                idx2unique{i,1} = idx2temp{i};
                D2unique{i,1} = D2temp{i};
            end
        end

        % Place unique matches in curated points list
        % Remove points from not uniquely matched list
        [idxcurated{1:length(idx), 1}] = deal(zeros(1,1));
        [idx2curated{1:length(idx2), 1}] = deal(zeros(1,1));
        counter = 1;
        if length(idx2unique)>length(idxunique)
            for i = 1:length(idx2unique)
                if length(idx2unique{i})==1 && logical(sum(idxunique{idx2unique{i}} == i)) && length(idxunique{idx2unique{i}}) == 1
                    idx2curated{i} = idx2unique{i};
                    idxcurated{idx2unique{i}} = idxunique{idx2unique{i}};
                    D2unique{i} = [];
                    Dunique{idx2unique{i}} = [];
                    idxunique{idx2unique{i}} = [];
                    idx2unique{i} = [];
                    pair(counter,2) = idx2curated{i};
                    pair(counter,1) = i;
                    counter = counter +1;
                end
            end
        else
            for i = 1:length(idxunique)
                if length(idxunique{i})==1 && logical(sum(idx2unique{idxunique{i}} == i)) && length(idx2unique{idxunique{i}}) == 1
                    idxcurated{i} = idxunique{i};
                    idx2curated{idxunique{i}} = idx2unique{idxunique{i}};
                    Dunique{i} = [];
                    D2unique{idxunique{i}} = [];
                    idx2unique{idxunique{i}} = [];
                    idxunique{i} = [];
                    pair(counter,1) = idxcurated{i}; %dots1
                    pair(counter,2) = i; %dots2
                    counter = counter + 1;
                end
            end
        end

        idxmin = idxunique;
        Dmin = Dunique;
        for i = 1:length(idxunique)
            if length(Dunique{i}) > 1
                smallest = Dunique{i} == min(Dunique{i});
                if sum(smallest) == 1
                    idxmin{i,1} = idxunique{i}(smallest);
                    Dmin{i,1} = Dunique{i}(smallest);
                end
            end
        end

        idx2min = idx2unique;
        D2min = D2unique;
        for i = 1:length(idx2unique)
            if length(D2unique{i}) > 1
                smallest = D2unique{i} == min(D2unique{i});
                if sum(smallest) == 1
                    idx2min{i,1} = idx2unique{i}(smallest);
                    D2min{i,1} = D2unique{i}(smallest);
                end
            end
        end

        if length(idx2min)>length(idxmin)
            for i = 1:length(idx2min)
                if length(idx2min{i})==1 && length(idxmin{idx2min{i}}) == 1
                    if idxmin{idx2min{i}} == i
                        idx2curated{i} = idx2min{i};
                        idxcurated{idx2min{i}} = idxmin{idx2min{i}};
                        D2min{i} = [];
                        Dmin{idx2min{i}} = [];
                        idxmin{idx2min{i}} = [];
                        idx2min{i} = [];
                        pair(counter,2) = idx2curated{i};
                        pair(counter,1) = i;
                        counter = counter +1;
                    else
                        idx2min{i} = [];
                        D2min{i} = [];
                    end
                elseif length(idx2min{i})==1 && isempty(idxmin{idx2min{i}})
                    idxmin{i} = [];
                    Dmin{i} = [];
                end
            end
        else
            for i = 1:length(idxmin)
                 if length(idxmin{i})==1 && length(idx2min{idxmin{i}}) == 1
                    if idx2min{idxmin{i}} == i
                        idxcurated{i} = idxmin{i};
                        idx2curated{idxmin{i}} = idx2min{idxmin{i}};
                        Dmin{i} = [];
                        D2min{idxmin{i}} = [];
                        idx2min{idxmin{i}} = [];
                        idxmin{i} = [];
                        pair(counter,2) = i;
                        pair(counter,1) = idxcurated{i};
                        counter = counter +1;
                    else
                        idxmin{i} = [];
                        Dmin{i} = [];
                    end
                 elseif length(idxmin{i})==1 && isempty(idx2min{idxmin{i}})
                    idxmin{i} = [];
                    Dmin = [];
                end
            end
        end

        idxz = idxmin;
        for i = 1:length(idxz) 
            if length(idxz{i}) > 1 
                zref = dots2(i,3);
                zdots = dots1(idxmin{i}, 3);
                keepers = zdots == zref;
                dummy = idxz{i};
                idxz{i} = dummy(keepers);
            end 
        end

        idx2z = idx2min;
        for i = 1:length(idx2z) 
            if length(idx2z{i}) > 1 
                zref = dots1(i,3);
                zdots = dots2(idx2min{i}, 3);
                keepers = zdots == zref;
                dummy = idx2min{i};
                idx2z{i} = dummy(keepers);
            end 
        end

        if length(idx2z)>length(idxz)
            for i = 1:length(idx2z)
                if length(idx2z{i})==1 && length(idxz{idx2z{i}}) == 1
                    if idxz{idx2z{i}} == i
                        idx2curated{i} = idx2z{i};
                        idxcurated{idx2z{i}} = idxz{idx2z{i}};
                        idxz{idx2z{i}} = [];
                        idx2z{i} = [];
                        pair(counter,2) = idx2curated{i};
                        pair(counter,1) = i;
                        counter = counter +1;
                    else
                        idx2z{i} = [];
                    end
                elseif length(idx2z{i})==1 && isempty(idxz{idx2z{i}})
                    idx2z{i} = [];
                elseif length(idx2z{i})>1
                    len = cellfun(@length,idxz(idx2z{i}));
                    if sum(len) == 1
                        keepers = len' == 1;
                        vals = idx2z{i}(keepers);
                        idx2curated{i} = vals;
                        idxcurated{vals} = idxz{vals};
                        idx2z{i} = [];
                        idxz{vals} = [];
                        pair(counter,2) = idx2curated{i};
                        pair(counter,1) = i;
                        counter = counter +1;
                    end     
                end
            end
        else
            for i = 1:length(idxz)
                 if length(idxz{i})==1 && length(idx2z{idxz{i}}) == 1
                    if idx2z{idxz{i}} == i
                        idxcurated{i} = idxz{i};
                        idx2curated{idxz{i}} = idx2z{idxz{i}};
                        idx2z{idxz{i}} = [];
                        idxz{i} = [];
                        pair(counter,2) = i;
                        pair(counter,1) = idxcurated{i};
                        counter = counter +1;
                    else
                        idxz{i} = [];
                    end
                elseif length(idxz{i})==1 && isempty(idx2z{idxz{i}})
                    idxz{i} = [];
                elseif length(idxz{i})>1
                    len = cellfun(@length,idx2z(idxz{i}));
                    if sum(len) == 1
                        keepers = len' == 1; 
                        vals = idxz{i}(keepers);
                        idxcurated{i} = vals;
                        idx2curated{vals} = idx2z{vals};
                        idxz{i} = [];
                        idx2z{vals} = [];
                        pair(counter,2) = i;
                        pair(counter,1) = idxcurated{i};
                        counter = counter +1;
                    end
                end
            end
        end

        %%%% added to remove multiple matching
        for i = 1:length(idxz)
            if length(idxz{i})>1
                a = idx2z(idxz{i});
                for j = length(a):-1:1
                    if length(a{j}) == 1 && a{j} ~= i
                        idxz{i}(j) = [];
                    elseif isempty(a{j})
                        idxz{i}(j) = [];
                    end
                end
            end
        end

        for i = 1:length(idx2z)
            if length(idx2z{i})>1
                a = idxz(idx2z{i});
                for j = length(a):-1:1
                    if length(a{j}) == 1 && a{j} ~= i
                        idx2z{i}(j) = [];
                    elseif isempty(a{j})
                        idx2z{i}(j) = [];
                    end
                end
            end
        end
        %%%%%

        %% Get Pairs for idxz and idx2z
        % what is this used for?

        if length(idxz)>length(idx2z)
            for i = 1:length(idxz)
                if ~isempty(idxz{i}) 
                        if length(idxz{i}) ==1 && length(idx2z{idxz{i}}) == 1 && idx2z{idxz{i}} == i %~isempty(idx2z{idxz{i}})
                            pair(counter,2) = i;
                            pair(counter,1) = idxz{i};
                            idx2z{idxz{i}} = [];
                            idxz{i} = [];
                            counter = counter + 1;
                        end
                end
            end
        else
            for i = 1:length(idx2z)
                if ~isempty(idx2z{i}) 
                    if i == 4124
                        disp('stop');
                    end
                        if length(idx2z{i}) == 1 && length(idxz{idx2z{i}}) == 1 && idxz{idx2z{i}} == i %~isempty(idxz{idx2z{i}})
                            pair(counter,2) = idx2z{i};
                            pair(counter,1) = i;
                            idxz{idx2z{i}} = [];
                            idx2z{i} = [];
                            counter = counter + 1;
                        end
                end
            end
        end

        %{
        Take out for now
        for i = 1:length(idxz)
           if length(idxz{i}) > 1
               bart = points(hybnum).dots(channels(1)).intensity(idxz{i}) == max(points(hybnum).dots(channels(1)).intensity(idxz{i}));
               if sum(bart) > 1
                   bart = false(1,length(bart));
                   bart(1) = 1;
               end
               pair(counter,2) = i;
               pair(counter,1) = idxz{i}(bart');
               idxz{i} = [];
               counter = counter + 1;
           end
        end

        for i = 1:length(idx2z)
           if length(idx2z{i})==1 && isempty(idxz{idx2z{i}})
               idx2z{i} = [];
           elseif length(idx2z{i}) > 1
               bart = points(hybnum2).dots(channels(2)).intensity(idx2z{i}) == max(points(hybnum2).dots(channels(2)).intensity(idx2z{i}));
               if sum(bart) > 1
                   bart = false(1,length(bart));
                   bart(1) = 1;
               end
               pair(counter,2) = idx2z{i}(bart');
               pair(counter,1) = i;
               idx2z{i} = [];
               counter = counter + 1;
           end
        end
        %}

        %remove this for barcoding

        if ~isempty(pair)

            called1 = zeros(size(dots1,1),1);
            called1(pair(:,1)) = 1;
            called1 = logical(called1);
            called2 = zeros(size(dots2,1),1);
            called2(pair(:,2)) = 1;
            called2 = logical(called2);

            %2D gaussian mixture model scaled by intensity


            %Fit a known barcode
                pts1 = dots1(pair(:,1),:);
                pts2 = dots2(pair(:,2),:);
        end
    else
        called1 = zeros(size(dots1,1),1);
        called2 = zeros(size(dots2,1),1);
        pair = [];
        pts1 = [];
        pts2 = [];
    end

    if isempty(pair)
        called1 = zeros(size(dots1,1),1);
        called2 = zeros(size(dots2,1),1);
        pair = [];
        pts1 = [];
        pts2 = [];
    end

    %image ouput of colocalization
    if debug == 1
        figure;
        g(1:length(pts1), 1) = 1;
        g(length(pts1)+1:2*length(pts1), 1) = 2;
        vec = pts2 - pts1;
        allpts = [pts1;pts2];
        z = allpts(:,3);
        % call GSCATTER and capture output argument (handles to lines)
        h = gscatter(allpts(:,1), allpts(:,2), g,[],'ox+*sdv^<>ph.',5);
        % for each unique group in 'g', set the ZData property appropriately
        gu = unique(g);
        for k = 1:numel(gu)
              set(h(k), 'ZData', z( g == gu(k) ));
        end
        view(3)
        hold on; quiver3(pts1(:,1),pts1(:,2),pts1(:,3),vec(:,1),vec(:,2),vec(:,3),0,'MaxHeadSize',0.5)
        figure; ax = axes; showMatchedFeatures(max(image1,[],3), max(image2,[],3), pts1(:,1:2), pts2(:,1:2));
        legend(ax,'dots 1','dots 2');
        hold on
    end
end

