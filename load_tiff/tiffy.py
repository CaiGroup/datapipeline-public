import numpy as np
import tifffile

def load(tiff_src):    
    
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
        num_of_wavelengths = 4

        total_channels_times_z_stacks = tiff.shape[0]

        num_of_z = total_channels_times_z_stacks/num_of_wavelengths

        print(f'{num_of_z=}')

        assert num_of_z == int(num_of_z), "The tiff file is not organized correctly."

        num_of_z = int(num_of_z)
        #---------------------------------------------------------------------
        
        #Get Indexes
        #---------------------------------------------------------------------
        indexes = np.zeros((tiff.shape[0]))
        list_of_numbers = np.asarray(range(tiff.shape[0])).reshape((num_of_z, num_of_wavelengths))

        for i in range(num_of_z):
            indexes[i::num_of_z] = list_of_numbers[i]

        indexes = indexes.astype(np.int32)
        #---------------------------------------------------------------------
        
        #Reorder and reshape
        #---------------------------------------------------------------------
        reordered_tiff = tiff[indexes]

        x_len =tiff.shape[1]
        y_len = tiff.shape[2]

        reshaped_tiff = reordered_tiff.reshape(num_of_z, num_of_wavelengths, x_len, y_len) 
        #---------------------------------------------------------------------
        
        return reshaped_tiff
    
    else:
        raise Exception("The tiff shape is weird!!!!!!!!")

