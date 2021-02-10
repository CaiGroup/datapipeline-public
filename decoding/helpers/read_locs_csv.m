function [spot_locations, spot_intensity] = read_locs_csv(csv_src)
    locs = readtable(csv_src);
    locs.ch = categorical(locs.ch);
    locs.hyb = categorical(locs.hyb);

    spot_locations = {};
    spot_intensity = {};
    hybs = unique(locs.hyb);
    chs = unique(locs.ch);
    for i = 1:length(hybs)
        for j = 1:length(chs)
            indexes = (locs.hyb == hybs(i)) & (locs.ch == chs(j));
            locs_ch = locs(indexes,:);
            points_ch = table2array(locs_ch(:,3:5));
            intensity_ch = table2array(locs_ch(:,6));
            spot_locations{end+1} = points_ch;
            spot_intensity{end+1} = intensity_ch;
        end
    end
end