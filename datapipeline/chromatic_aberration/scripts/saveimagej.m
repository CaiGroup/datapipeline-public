function saveimagej(L, savePath)
% function to save the segmentation masks as ome-tif files
%
% date: 3/12/2020

    % start imageJ
    Miji(false);
    namesh = 'L.tif';
    % try to save
    try
        MIJ.createImage(namesh, L, true);
        MIJ.run('Save', ['save=[' savePath '.tif' ']']);
        MIJ.run('Close All')
    catch
        MIJ.exit;
        error('MIJ exited incorrectly\n');
    end

end