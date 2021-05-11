import numpy as np
import tifffile

def load(tiff_src, num_wav=4, num_z=None):    
    print(f'{tiff_src=}')
    
    print(f'{num_wav=}')
    
    #Read tiff file
    #---------------------------------------------------------------------
    tiff = tifffile.imread(tiff_src)
    print(f'{tiff.shape=}')
    print(f'{num_z=}')
    print(f'{type(num_z)=}')
    #---------------------------------------------------------------------
    
    #Raise assertion to check that x and y are equal length 
    #---------------------------------------------------------------------
    assert tiff.shape[-1] == tiff.shape[-2]
    #---------------------------------------------------------------------
    
    if num_z == 'None':
        num_z=None
    
    #Checks if tiff is read normally
    #---------------------------------------------------------------------
    if len(tiff.shape)==4:
        
        #Checks if channels is meant to be 4
        #assert tiff.shape[1]==4
        print(f'{tiff.shape=}')
        assert tiff.shape[1] == float(num_wav)
        
        
        return tiff
    #---------------------------------------------------------------------
    
    elif num_z != None and len(tiff.shape)==3:
        tiff_new_dim = tiff[np.newaxis, ...]
        return tiff_new_dim
    
    #Checks if tiff is (channels*z stacks, 2048, 2048)
    #---------------------------------------------------------------------
    elif len(tiff.shape)==3:
        
        
        #Define the variables needed
        #---------------------------------------------------------------------
        num_of_wavelengths = int(float(num_wav))

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

# from PIL import Image, ImageSequence
# import numpy as np

# def open_tiff_file(tiff_src, h=2048, w=2048):
#     im_lb = Image.open(tiff_src)
#     tiffarray = np.zeros((h,w,im_lb.n_frames))
#     for i, page in enumerate(ImageSequence.Iterator(im_lb)):
#         tiffarray[:,:,i] = np.asarray(page)   
        
#     tiff_swap1 = np.swapaxes(tiffarray, 0, 2)
#     tiff_swap2 = np.swapaxes(tiff_swap1, 1, 2)
#     return tiff_swap2

# def reorganize_by_channel(tiff, num_channels):
#     total_channels = 3
#     tiff_reshaped = []
#     for i in range(num_channels):
#         z_s_per_channel = int(tiff.shape[0]/num_channels)
#         print(f'{z_s_per_channel=}')
#         tiff_reshaped.append(tiff[(i)*z_s_per_channel:(i+1)*z_s_per_channel])
#     tiff_reshaped = np.array(tiff_reshaped)
#     tiff_reshaped = np.swapaxes(tiff_reshaped, 0, 1)
    
#     return tiff_reshaped

# def load(tiff_src, num_wav, num_z=None):
    
#     if type(num_wav) == float:
#         num_wav = int(num_wav)
#     elif type(num_wav) == str:
#         num_wav = int(float(num_wav))
#     elif type(num_wav) == int:
#         pass
#     else:
#         raise Exception("The data type for num wav is set incorrectly.")
        
#     #Outputs tiff in (n, 2048, 2048)
#     tiffarray = open_tiff_file(tiff_src)
    
#     #Outputs tiff in (z, ch, 2048, 2048)
#     tiff_reshaped = reorganize_by_channel(tiffarray, num_wav)
    
#     return tiff_reshaped
