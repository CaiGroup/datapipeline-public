locations_src = '/groups/CaiLab/analyses/nrezaee/2020-07-29-nrezaee-test1/dot/MMStack_Pos0/locations.mat'

radius = 3 

[number_of_matches, coloc_rate1, coloc_rate2, dots1] = main_coloc(locations_src, radius)

save('number_of_matches.mat', 'number_of_matches')