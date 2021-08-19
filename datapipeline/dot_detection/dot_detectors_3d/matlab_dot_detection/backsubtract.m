  
function I = backsubtract(hybimage, backimage, experimentDir)
% function divides the image by the background image and multiplies the
% median of the background image.
%
% Used for removing autofluorescent background
%
% Date: 8/9/2019

    %medianBack = median(backimage(:));

    hybimage = medfilt3(hybimage,[3 3 3]);
    backimage = medfilt3(backimage,[3 3 3]);
    imageTemp = (double(hybimage) ./ double(backimage));
    %imageTemp = (double(hybimage) ./ double(backimage));
    I = uint16(imageTemp .* 10000); % keep 4 places of decimals
    %I = imageTemp .* double(medianBack);

end