function [colocalizationData, points1, points2, threshold1, threshold2] = colocalizecheck(image1, image2, options)
% calculates the standard error and full half width maximum (FHWM) standard
% deviation error between the points in two images for localization and
% intensity values. FHWM = 2.355 * std
%
%
% Dependencies: 
% - Fiji.app/scripts directory
% - mij.jar: function asks for location for ImageJ
% - FindThreshold package
%
% Path examples:
% >> addpath('C:\Users\nicog\Documents\fiji-win64\Fiji.app\scripts\', '-end');
% >> baseDir = 'C:\github\seqfish';
% >> javaaddpath(fullfile(baseDir, 'io', 'bfmatlab', 'bioformats_package.jar'));
%
% Example of setting up struct for options:
%    >> options.return = true; % return colocalizationData, points, and
%    threshold
%    >> % set the radius, type of spot detection
%    >> options.radius = 3; % default is 1.76
%    >> options.dotdetect = 'log';
%    >> options.savefigs = true;
%    >> options.threshold1 = 800; % set numeric threshold value image1
%    >> options.threshold2 = 'choose'; % default already: choose threshold
%    value for image 2
%    >> options.processimages = true;
%
% Author: Nico Pierson
% nicogpt@caltech.edu
% Date: 1/28/2019
% Modified: 2/26/2019
% Options, try and catch code adapted from 'loadtiff.m' by YoonOh Tak 2012

    % use errcode to output different types of errors
    errcode = -1;
    try
    %% Check options structure for extra data
        if isreal(image1) == false || isreal(image2) == false
            errcode = 1; assert(false);
        end
        if nargin < 3
            options.savefigs = false;
            options.processimages = false;
            options.debugimages = false;
            options.tform = [];
            options.threshold1 = 'choose';
            options.threshold2 = 'choose';
            options.typedetectdots = 'log'; % options are 'exons' or 'introns'
            options.radius = 1.73; % default 1; colocalize dots in this pixel radius
            options.intarearadius = 3; % default is 3; compare intensity areas in this pixel radius
            options.gaussian = false; % option to use gaussian curve to fit dot locations
            options.return = false; % option for returning colocalization data or not
            options.align = false; % align the images 
            options.foldername = 0; % name of figure in manualthreshold
            options.channelname = 0; % name of figure in manualthreshold
            options.savefig = false; % save figure in manualthreshold
            options.savefigpath = ''; % save figure path in manualthreshold
            options.gatefigs = false; % optional figures
            options.printoutput = true; % print to the command window
        end
        if isfield(options, 'savefigs') == 0
            options.savefigs = false;
        end
        if isfield(options, 'processimages') == 0
            options.processimages = false;
        end
        if isfield(options, 'debugimages') == 0
            options.debugimages = false;
        end
        if isfield(options, 'tform') == 0
            options.tform = [];
        end
        if isfield(options, 'threshold1') == 0
            options.threshold1 = 'choose';
        end
        if isfield(options, 'threshold2') == 0
            options.threshold2 = 'choose';
        end
        if isfield(options, 'typedetectdots') == 0
            options.typedetectdots = 'log';
        end
        if isfield(options, 'radius') == 0
            options.radius = 1.73;
        end
        if isfield(options, 'intarearadius') == 0
            options.intarearadius = 3;
        end
        if isfield(options, 'gaussian') == 0
            options.gaussian = false;
        end
        if isfield(options, 'return') == 0
            options.return = false;
        end
        if isfield(options, 'align') == 0
            options.align = false;
        end
        if isfield(options, 'foldername') == 0
            options.foldername = 0;
        end
        if isfield(options, 'channelname') == 0
            options.channelname = 0;
        end
        if isfield(options, 'savefig') == 0
            options.savefig = false;
        end
        if isfield(options, 'savefigpath') == 0
            options.savefigpath = '';
        end
        if isfield(options, 'gatefigs') == 0
            options.gatefigs = false;
        end
        if isfield(options, 'printoutput') == 0
            options.printoutput = true; % print to the command window
        end

        
        %% Start finding the location and intensity error
        % Get date to save files for unique string
        dateStart = datetime;
        formatDate = 'yyyy-mm-dd';
        dateSaveString = datestr(dateStart, formatDate);
        fprintf('Started colocalizecheck.m on %s\n', dateSaveString);

        
        %% Declare Variables
        findThresholdFolderName = 'FindThreshold';
        zSlices = size(image1, 3);

        
        %% Option to Process Images
        % Use ImageJ Background Selection
        if options.processimages
            
            % Subtract the background
            image1Process = imagejbackgroundsubtraction(image1);
            image2Process = imagejbackgroundsubtraction(image2);
        end

        % Need to keep processed images for dot finding and original image
        % for intensities: no problems for intron finding dots, but it is a
        % problem for finding exons part

        %% Option to Find the threshold for each Set of Images
        threshold1Image = image1;
        threshold2Image = image2;
        if strcmp(options.threshold1, 'choose')
            disp('Choose a threshold for first Image');
            % add path to threshold
            addpath(['..' filesep findThresholdFolderName], '-end'); % change to finding the directory
            disp('Finding Threshold');
            % Process Image First with regional maxima and a lap filter for
            % 'exons' type of dot detection
            if options.processimages
                threshold1Image = image1Process;
            end
            [regMax, logFish] = preprocessdots(threshold1Image, options.typedetectdots);
            % Get first threshold
            threshold1 = manualthreshold(options.foldername, options.channelname, ... % set channel and folder to 0 for null
               threshold1Image, regMax, logFish, options.typedetectdots);
           disp('Completed Threshold for Image 1');
        else
            if isnumeric(options.threshold1)
                threshold1 = options.threshold1;
            else
                errcode = 3; assert(false);
            end
        end
        % Option to Find Second Threshold Value in the Image
        if strcmp(options.threshold2, 'choose')
            disp('Choose a threshold for the second Image');
            % add path to threshold
            addpath(['..' filesep findThresholdFolderName]);
            disp('Finding Threshold');
            % Process Image First with regional maxima and a lap filter for
            % 'exons' type of dot detection
            if options.processimages
                threshold2Image = image2Process;
            end
            [regMax, logFish] = preprocessdots(threshold2Image, options.typedetectdots);
            % Get second threshold
            threshold2 = manualthreshold(options.foldername, options.channelname, ...
                threshold2Image, regMax, logFish, options.typedetectdots);% set channel and folder to 0 for null
            disp('Completed Threshold for Image 2');
        else
            if isnumeric(options.threshold2)
                threshold2 = options.threshold2;
            else
                errcode = 3; assert(false);
            end
        end
        
        
        
        %% Find the Dots and Calculate the Error with the Mean
        % Images will either be the raw image or the process image
        disp('Preprocessing First Image');
        [dots1, dotsLogic1, lapImage1] = detectdotsv2(threshold1Image, threshold1, ...
            options.typedetectdots, options.debugimages, options.savefigpath);
        disp('Preprocessing Second Image');
        options.savefigpath = [options.savefigpath '-2'];
        [dots2, dotsLogic2, lapImage2] = detectdotsv2(threshold2Image, threshold2, ...
            options.typedetectdots, options.debugimages, options.savefigpath);
        
        
        

        %% Colocalize the dots
        % images only used for debugging purposes
        debug = 0;
        [points1, points2, ~, ~, ~] = colocalizedots(image1, ...
            image2, dots1, dots2, options.radius, debug);
        
        %% Get the raw areas for the intensity
        rawIntData1 = getrawintensity(points1, image1, options.intarearadius);
        rawIntData2 = getrawintensity(points2, image2, options.intarearadius);
        rawData1 = [points1(:,2), points1(:,1), points1(:,3), rawIntData1];
        rawData2 = [points2(:,2), points2(:,1), points2(:,3), rawIntData2];
        
        
        %% Print the Figures and get Error Values
        % Gaussian Fit points are used to calculate the location error
        [rIntPeak, rIntArea, fwhmLocation, fwhmIntPeak, fwhmIntArea] = printerrorfigures(rawData1, rawData2, zSlices, options.gatefigs);
        errorData = [rIntPeak, rIntArea, fwhmLocation, fwhmIntPeak, fwhmIntArea];
        
        
        if options.printoutput
            %% Print Output of all Variables
            numDots1 = size(dots1, 1);
            numDots2 = size(dots2, 1);
            numColDots = size(points1, 1);
            numberOfDots = [numDots1, numDots2, numColDots];
            thresholdData = [threshold1 threshold2];
            colocalizationData = printimageoutputs(rawData1, rawData2, numberOfDots, errorData, thresholdData);

            if ~options.return 
                % set to null if not using
                colocalizationData = [];
                points1 = [];
                points2 = [];
                threshold1 = [];
                threshold2 = [];
            end
        end

        disp('colocalizecheck.m function Complete');
        
    catch exception
        %% catch the exceptions in the function
        % Update the error messages for errors
        switch errcode
            case 0
                error 'Invalide path.';
            case 1
                error 'It does not support complex numbers.';
            case 2
                error '''data'' is empty.';
            case 3
                error 'Threshold option is invalid. Usage: enter numeric value or "choose" for options.threshold1 or 2';
            otherwise
                rethrow(exception);
        end
    end

end