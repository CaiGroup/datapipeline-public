function [] = saveimagecheckbypos(imageCheck, saveDir, saveName)
% saves the tif images used as alignment checks, save only 5 zslices in
% the middle of the tif file
%
% Date: 3/20/2020
% Author: Nico Pierson
% Email: nicogpt@caltech.edu

            
   %% check the final processed IF data
    I = imshrinkcell(imageCheck);
    
    % save by image for each channel and hyb
    saveimagecheckbyhyb(I,saveDir,saveName,'');

end