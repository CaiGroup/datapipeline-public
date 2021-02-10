function [consensuscell, copynumfinal ] = decoding(barcode_src, locations_src, dest, num_of_rounds, total_num_of_channels, allowed_diff, minseeds)  
    
    warning('off','all')
    
    
    disp('This is the allowed diff')
    disp(allowed_diff)
    %Loading .mats
    %-----------------------
    disp("Reading Points")
    disp(locations_src)
    location_variables = load(locations_src)
    
    spotslocation = location_variables.points
    
    spotsintensity = location_variables.intensity;

    
    disp(barcode_src)
    barcodekey_info = load(barcode_src)
    barcodekey = barcodekey_info.barcodekey.barcode;
    %-----------------------
    
    
    %Set Variables for point structure function
    %--------------------------------------------------------------------
    spotsintensityscaled = [];
    
    numPseudoChannels = total_num_of_channels/num_of_rounds;

    z_slice = [];
    %--------------------------------------------------------------------
    
    

    %Get Points in Correct format
    %--------------------------------------------------------------------
    [points, numpointspercell] = orgcell2points(spotslocation, spotsintensity, spotsintensityscaled, num_of_rounds, numPseudoChannels, z_slice);
    %--------------------------------------------------------------------
    
    disp(points)
    
    %Set variables for Decoding Function
    %--------------------------------------------------------------------
    %Number of Channels in each round
    channels = numPseudoChannels;
    
    %Radius for colocalization
    radius = sqrt(3);
    
    %Difference allowed in barcode
   % alloweddiff = 1;
    
   % minseeds = num_of_rounds - 1;
   
    disp("before if")
    minseeds
   
    if strcmp(minseeds, 'number_of_rounds - 1')
        minseeds = num_of_rounds - 1
        disp('hi')
    else
        minseeds = str2double(minseeds)
    end
    %--------------------------------------------------------------------
    
    
    %Runs the Decoding
    %--------------------------------------------------------------------
    [consensuscell, copynumfinal ] = BarcodeNoMiji_v8( numPseudoChannels, points, num_of_rounds, barcodekey,radius,allowed_diff);
    
    [dotlocations_unfiltered] = PointLocations_v2(num_of_rounds, channels, points, consensuscell,copynumfinal, radius);



    cc_path = fullfile(dest, 'consensuscell.mat')
    save(cc_path, 'consensuscell') 
    
    cnf_path = fullfile(dest, 'copynumfinal.mat')
    save(cnf_path, 'copynumfinal')

    dotlocations_unfiltered_path = fullfile(dest, 'dotlocations_unfiltered.mat')
    save(dotlocations_unfiltered_path, 'dotlocations_unfiltered') 
    
    [seeds] = numseeds(dotlocations_unfiltered);

    [finalPosList, PosList, dotlocations] = filterseeds_v3(seeds, dotlocations_unfiltered, minseeds);
    %--------------------------------------------------------------------
    
    
    %Convert Dotlocations2table
    %--------------------------------------------------------------------
    [dotlocations_table_filtered, dotlocations_table_unfiltered] = dotlocations2table(dotlocations, barcodekey_info.barcodekey.names, minseeds);
    %--------------------------------------------------------------------
    
    %dotlocations_table = table2cell(dotlocations_table)

    %Save results
    %--------------------------------------------------------------------
    table_filt_file_name = strcat('pre_seg_diff_', int2str(allowed_diff),'_minseeds_', int2str(minseeds), '_filtered.csv')
    table_unfilt_file_name = strcat('pre_seg_diff_', int2str(allowed_diff),'_minseeds_', int2str(minseeds), '_unfiltered.csv')
    dotlocations_filt_table_path = fullfile(dest, table_filt_file_name)
    dotlocations_unfilt_table_path = fullfile(dest, table_unfilt_file_name)
    
    finalPosList_path = fullfile(dest, 'finalPosList.mat')
    PosList_path = fullfile(dest, 'PosList.mat')
    seeds_path = fullfile(dest, 'seeds.mat')
    dotlocations_path = fullfile(dest, 'dotlocations.mat')
    
    
    %writetable(dotlocations_table, dotlocations_table_path)
    writetable(dotlocations_table_unfiltered, dotlocations_unfilt_table_path)
    writetable(dotlocations_table_filtered, dotlocations_filt_table_path)
    save(dotlocations_path, 'dotlocations') 
    save(finalPosList_path, 'finalPosList')                                  
    save(PosList_path, 'PosList')
    save(seeds_path, 'seeds')
    %--------------------------------------------------------------------

end









