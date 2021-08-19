function [dotlocations,seeds] = BarcodeFinder(channels, points, hyb, barcodekey,radius,alloweddiff)
%#codegen
% decodes the barcoded images with the number of channels, the points, the 
% nubmber of rounds, barcodekey, search radius and number of barcode rounds 
% needed to decode a gene (alloweddiff).
%
% channels = number of pseudocolors
% hyb = number of rounds
% points = point structure
% radius = will square root in the function
% alloweddiff = allowed number of rounds for error correction
%
% Debugging: the false positive rate
%
% Author: Sheel Shah
% Date: 8/4/2019

[consensuscell,copynumfinal ] = BarcodeNoMiji_v8( channels, points, hyb, barcodekey,radius,alloweddiff);

[dotlocations] = PointLocations(hyb, channels, points, consensuscell,copynumfinal, radius);

[seeds] = numseeds(dotlocations);

end

