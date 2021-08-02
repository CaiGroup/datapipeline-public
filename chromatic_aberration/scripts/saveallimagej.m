function saveallimagej(I, savePath) 
% save all hybs and channels as a tiff

    numCh = size(I,2);
    numHybs = size(I,1);
    numZSlice = size(I{1}, 3);
    numTotalGenes = numCh * numHybs;
    % reorganize
    I = stackrows(I);
    
    Miji(false);
    
    iter = 1;
    for f = 1:numTotalGenes
        namesh{iter} = ['C' num2str(f) '-'  num2str(1) '.tif'];
        MIJ.createImage(namesh{iter}, I{f}, true);
        iter = iter + 1;
    end


    %% Need to break up the images, because there are too many, break into 4 separate images
    str = [];
    iter = 1;
    for f = 1:numTotalGenes
        str = [str ' image' num2str(iter) '=C' num2str(f) '-' num2str(1) '.tif'];
        iter = iter + 1;
    end


    try
        if numHybs > 1
            MIJ.run('Concatenate...', ['  title=[Concatenated Stacks] open' str]);
        end
        MIJ.run('Stack to Hyperstack...', ['order=xyzct channels=' num2str(numTotalGenes) ' slices=' num2str(numZSlice) ' frames=1 display=Grayscale']);
        MIJ.run('Save', ['save=[' savePath '.tif' ']']);
        MIJ.run('Close All')
        MIJ.exit;
    catch
        MIJ.exit;
        error('MIJ exited incorrectly: most likely caused by out of memory in the java heap\n');
    end
end
        