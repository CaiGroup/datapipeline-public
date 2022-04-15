function processed_img = process_img(image, varargin)
    blur = imgaussfilt3(image, 3);

    roll_sub = image - blur;
    
    se = strel('disk',12);
    
    processed_img = imtophat(roll_sub,se);
end
