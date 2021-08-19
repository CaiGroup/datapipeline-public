function [number_of_matches, coloc_rate1, coloc_rate2, dots1] = get_matched_dots(image1_src, image2_src, threshold, radius, debug)
    % [number_of_matches, coloc_rate1, coloc_rate2, dots] = get_matched_dots('C:\Users\Nick Rezaee\Documents\cai-lab\align_for_linus\data\rca_hyb2_200ms_1_MMStack_Pos3.ome.tif', 'C:\Users\Nick Rezaee\Documents\cai-lab\align_for_linus\data\rca_hyb2_200ms_afterstripped_restain_smfish_4s_1_MMStack_Pos3.ome.tif', 5000, 3, 0)
    %inputs:
    %   image1_src  -- source of first image
    %   image2_src  -- source of second image
    %   threshold      -- threshold 
    %   radius           -- radius 
    
    %outputs
    %   number_of_matches   -- number of matched dots
    %   coloc_rate1                 -- colocalization rate of first image
    %   coloc_rate2                 -- colocalization rate of second image
    
    t1 = Tiff(image1_src,'r');
    t2 = Tiff(image2_src,'r');

    imageData1 = read(t1);
    imageData2 = read(t2);

    
    [dots1, intensity1, dotsLogical1, logimage1]  =detectdotsv2(imageData1, threshold);
    [dots2, intensity2, dotsLogical2, logimage2]  =detectdotsv2(imageData2, threshold);

    [pts1, pts2, called, called2, pair] = colocalizedots(imageData1, imageData2, dots1, dots2, radius, debug);

    number_of_matches = length(pair)
    
    coloc_rate1 =  number_of_matches/length(dots1)
    coloc_rate2 =  number_of_matches/length(dots2)
end
    
    