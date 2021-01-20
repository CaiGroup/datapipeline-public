function [number_of_matches, coloc_rate1, coloc_rate2] = main_coloc(locations_src, dest, radius)
    
    warning('off','all')'
    
    locations = load(locations_src).locations;
    
    dots1 = locations{1,1,:};

    dots2 = locations{4,1,:};   
    
    
    [pts1, pts2, called, called2, pair] = colocalizedots(dots1, dots2, radius);

    number_of_matches = length(pair)
    
    coloc_rate1 =  number_of_matches/length(dots1)
    coloc_rate2 =  number_of_matches/length(dots2)
    
    coloc_results_path = fullfile(dest,'colocalization')
                                      
    save(coloc_results_path, 'number_of_matches', 'coloc_rate1', 'coloc_rate2')
end
    
