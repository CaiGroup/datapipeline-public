import numpy as np
import tifffile

def reshape_michal_tiffs(tiff):
    new_tiff = []
    new_tiff.append(tiff[:5])
    new_tiff.append(tiff[5:10])
    new_tiff.append(tiff[10:15])
    new_tiff = np.array(new_tiff)
    new_tiff = np.swapaxes(new_tiff, 0, 1)
    return new_tiff

def load(tiff_src, num_wav):    
    print(f'{tiff_src=}')
    
    #Read tiff file
    #---------------------------------------------------------------------
    tiff = tifffile.imread(tiff_src)
    #---------------------------------------------------------------------
    
    #Raise assertion to check that x and y are equal length 
    #---------------------------------------------------------------------
    assert tiff.shape[-1] == tiff.shape[-2]
    #---------------------------------------------------------------------
    
    #Checks if tiff is read normally
    #---------------------------------------------------------------------
    if len(tiff.shape)==4:
        
        #Checks if channels is meant to be 4
        #assert tiff.shape[1]==4
        
        return tiff
    #---------------------------------------------------------------------
    
    #Checks if tiff is (channels*z stacks, 2048, 2048)
    #---------------------------------------------------------------------
    elif len(tiff.shape)==3:
        
        
        #Define the variables needed
        #---------------------------------------------------------------------
        num_of_wavelengths = num_wav

        total_channels_times_z_stacks = tiff.shape[0]

        num_of_z = total_channels_times_z_stacks/num_of_wavelengths

        print(f'{num_of_z=}')

        assert num_of_z == int(num_of_z), "The tiff file is not organized correctly."

        num_of_z = int(num_of_z)
        #---------------------------------------------------------------------
        
        reshaped_tiff = tiff.reshape(num_of_z, num_of_wavelengths, tiff.shape[1], tiff.shape[2], order = 'F') 
        #---------------------------------------------------------------------
        
        return reshaped_tiff
    
    else:
        raise Exception("The tiff shape is weird!!!!!!!!")

