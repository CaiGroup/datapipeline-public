function [pointsSR] = SuperResPoints(points, hybnum,xyPixSize,zPixSize)
%#codegen
% takes 3x3 subset of the image and calculates the radial center super
% resolution of a point

pointsSR = points;
for i = 1:size(points,2)
    for j = 1:size(points{i},1)
        for k = size(points{i}(j).channels,1):-1:1
            [y,x,z] = size(hybnum(i).color{j});
            if points{i}(j).channels(k,2)-1 == 0 || points{i}(j).channels(k,2)+1 > y ||...
               points{i}(j).channels(k,1)-1 == 0 || points{i}(j).channels(k,1)+1 > x ||...
               points{i}(j).channels(k,3)-1 == 0 || points{i}(j).channels(k,3)+1 > z
                pointsSR{i}(j).channels(k,:) = [];
                pointsSR{i}(j).intensity(k,:) = [];
            else   
                I = hybnum(i).color{j}(points{i}(j).channels(k,2)-1:points{i}(j).channels(k,2)+1,...
                                       points{i}(j).channels(k,1)-1:points{i}(j).channels(k,1)+1,...
                                       points{i}(j).channels(k,3)-1:points{i}(j).channels(k,3)+1);
                [rc, sigma] = radialcenter3D(double(I), zPixSize/xyPixSize);
                rc([1 2]) = rc([2 1]);
                pointsSR{i}(j).channels(k,:) =((rc-[2;2;3]+points{i}(j).channels(k,:)').*[xyPixSize;xyPixSize;zPixSize])';
                pointsSR{i}(j).intensity(k) = sigma;
            end
        end
    end
end