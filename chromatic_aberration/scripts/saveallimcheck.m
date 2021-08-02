function [] = saveallimcheck(I, imageSaveDir, posArray)
% wrapper function to save all the image checks of images in a cell array
%
% date: 3/11/2020

    if exist(imageSaveDir,'dir') ~= 7
        mkdir(imageSaveDir);
    end
    for i = posArray
        startSaveName = ['image-check-pos' num2str(i)];
        savefolchimage(I{i+1},imageSaveDir,startSaveName,'');
    end
    
end