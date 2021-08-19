function [consensuscell, copynumfinal ] = decoding(barcode_src, locations_src, dest, num_of_rounds, total_num_of_channels, allowed_diff, minseeds)  
    
    warning('off','all')
    
    
    %Loading .mats
    %-----------------------
    disp("Reading Points")
    disp(locations_src)
    points = reshape(squeeze(struct2cell(load(locations_src).points)), [1 5])
    
    barcodekey = load(barcode_src).barcodekey.barcode;;
    %-----------------------
    

    %Get Points in Correct format
    %--------------------------------------------------------------------
    %[points, numpointspercell] = orgcell2points(spotslocation, spotsintensity, spotsintensityscaled, num_of_rounds, numPseudoChannels, z_slice);
    %--------------------------------------------------------------------
    
    
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
        minseeds = double(minseeds)
    end
    %--------------------------------------------------------------------
    
    
    %Runs the Decoding
    %--------------------------------------------------------------------
    [consensuscell, copynumfinal ] = BarcodeNoMiji_v8( numPseudoChannels, points, num_of_rounds, barcodekey,radius,allowed_diff);
    
    [dotlocations_unfiltered] = PointLocations(num_of_rounds, channels, points, consensuscell,copynumfinal, radius);



    cc_path = fullfile(dest, 'consensuscell.mat')
    save(cc_path, 'consensuscell') 
    
    cnf_path = fullfile(dest, 'copynumfinal.mat')
    save(cnf_path, 'copynumfinal')

    dotlocations_unfiltered_path = fullfile(dest, 'dotlocations_unfiltered.mat')
    save(dotlocations_unfiltered_path, 'dotlocations_unfiltered') 
    
    [seeds] = numseeds(dotlocations_unfiltered);

    [finalPosList, PosList, dotlocations] = filterseedsv2(seeds, dotlocations_unfiltered, minseeds);
    %--------------------------------------------------------------------
    

    %Save results
    %--------------------------------------------------------------------
    finalPosList_path = fullfile(dest, 'finalPosList.mat')
    PosList_path = fullfile(dest, 'PosList.mat')
    seeds_path = fullfile(dest, 'seeds.mat')
    dotlocations_path = fullfile(dest, 'dotlocations.mat')
    
    save(dotlocations_path, 'dotlocations') 
    save(finalPosList_path, 'finalPosList')                                  
    save(PosList_path, 'PosList')
    save(seeds_path, 'seeds')
    %--------------------------------------------------------------------

end






