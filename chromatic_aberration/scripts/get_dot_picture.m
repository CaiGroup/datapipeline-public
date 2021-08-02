function [dots] = get_dot_pictures(image_src, threshold)
    %inputs:
    %  image_src -- source of image
    %  threshold   -- the threshold for points
    %  radius
    
    %outputs:
    %  dots -- locations of the dots on the image
    

    t = Tiff(image_src,'r');
    imageData = read(t);

    [dots, intensity, dotsLogical, logimage]  =detectdotsv2(imageData, 19000);

    imshow(imadjust(imageData))
    hold on;
    for n = 1:length(dots)
       % disp(dots1(n,2))
       plot(dots(n,1), dots(n,2), 'r*', 'LineWidth', 2, 'MarkerSize', .1);
    end
    