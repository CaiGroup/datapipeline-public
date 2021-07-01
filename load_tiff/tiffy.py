import numpy as np
import tifffile as tf
from load_tiff.util import pil_imread

def load(tiff_src, num_wav=4, num_z=None):    
        
    try:
        tiff = pil_imread(tiff_src)
        
        tiff = np.swapaxes(tiff, 0, 1)
        
    except:
        
        tiff = tf.imread(tiff_src)
        
    return tiff
    
    # #Read tiff file
    # #---------------------------------------------------------------------
    # tiff = tifffile.imread(tiff_src)
    # #---------------------------------------------------------------------
    
    # #Raise assertion to check that x and y are equal length 
    # #---------------------------------------------------------------------
    # assert tiff.shape[-1] == tiff.shape[-2]
    # #---------------------------------------------------------------------
    
    # if num_z == 'None':
    #     num_z=None
    
    # #Checks if tiff is read normally
    # #---------------------------------------------------------------------
    # if len(tiff.shape)==4:
        
    #     #Checks if channels is meant to be 4
    #     #assert tiff.shape[1]==4
    #     assert tiff.shape[1] == float(num_wav)
        
        
    #     return tiff
    # #---------------------------------------------------------------------
    
    # elif num_z != None and len(tiff.shape)==3:
    #     tiff_new_dim = tiff[np.newaxis, ...]
    #     return tiff_new_dim
    
    # #Checks if tiff is (channels*z stacks, 2048, 2048)
    # #---------------------------------------------------------------------
    # elif len(tiff.shape)==3:
        
        
    #     #Define the variables needed
    #     #---------------------------------------------------------------------
    #     num_of_wavelengths = int(float(num_wav))

    #     total_channels_times_z_stacks = tiff.shape[0]

    #     num_of_z = total_channels_times_z_stacks/num_of_wavelengths
        
    #     assert num_of_z == int(num_of_z), "The tiff file is not organized correctly."

    #     num_of_z = int(num_of_z)
    #     #---------------------------------------------------------------------
        
    #     reshaped_tiff = tiff.reshape(num_of_z, num_of_wavelengths, tiff.shape[1], tiff.shape[2], order = 'F') 
    #     #---------------------------------------------------------------------
        
    #     return reshaped_tiff
    
    # else:
    #     raise Exception("The tiff shape is weird!!!!!!!!")
