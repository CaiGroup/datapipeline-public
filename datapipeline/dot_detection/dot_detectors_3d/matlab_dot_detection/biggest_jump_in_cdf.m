function [thresh_dots, thresh_intensity] = biggest_jump_in_cdf(intensity, dots, strictness, nbins, biggest_jump_fig_dst)

    %Get initial bin values
    %--------------------------------------
    [intensity,TF] = rmoutliers(intensity);
    hist = histogram(intensity, nbins);
    %--------------------------------------

    %Get reverse cumalative histogram
    %--------------------------------------
    [N,edges] = histcounts(intensity,nbins);
    cdf = cumsum(N, 'reverse');
    %--------------------------------------

    %Differences of each value
    %--------------------------------------
    diff_of_values = abs(diff(cdf));

    [max_value, max_index] = max(diff_of_values);
    
    max_index = max_index + strictness

    biggest_jump_thresh = edges(max_index);
    %--------------------------------------

    %Plot and save value
    %--------------------------------------
    fig = figure
    plot(cdf);
    xline(max_index);
    
    saveas(fig, biggest_jump_fig_dst);
    %--------------------------------------

    %Remove intensities based off thresh
    %--------------------------------------        
    thresh_ints_bools = intensity > biggest_jump_thresh;
    thresh_intensity = intensity(thresh_ints_bools);
    %--------------------------------------

    %Remove Dots based off intensities
    %---------------------------------------------
    thresh_ints_ind = find(thresh_ints_bools);
    size_dots = size(dots);

    all_indices = 1:size_dots(1);
    remove_inds = setdiff(all_indices,thresh_ints_ind);
    dots(remove_inds, :) = [];
    thresh_dots = dots;
    %---------------------------------------------

end