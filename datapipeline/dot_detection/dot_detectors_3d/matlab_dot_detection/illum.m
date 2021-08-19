  
function adjust = illum_correct(image)

    se = strel('disk',30)
    back = imopen(image,se);
    correct = image - back;
    adjust = imadjust3(correct);

end