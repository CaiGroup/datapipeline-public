import sys

import numpy as np
import tifffile as tf

try:
    from util import pil_imread
except:
    pass

try:
    from .util import pil_imread
except:
    pass


def load(tiff_src, num_wav=4, num_z=None, swapaxes=True):
    print(f'{tiff_src=}')

    try:
        # Read with Lincoln's function
        # ---------------------------------------------------------------------
        print("Reading with Lincoln's pil_imread")
        tiff = pil_imread(tiff_src, swapaxes=swapaxes)
        # ---------------------------------------------------------------------

        # Switch 1z if it is mixed up
        # ---------------------------------------------------------------------
        if tiff.shape[1] == 1:
            print('Swapping axes')
            tiff = np.swapaxes(tiff, 0, 1)
        # ---------------------------------------------------------------------

        # Check if channel and z need to be switched
        # ---------------------------------------------------------------------
        if tiff.shape[1] != num_wav:
            if tiff.shape[0] == num_wav:
                tiff = np.swapaxes(tiff, 0, 1)

        # ---------------------------------------------------------------------


    except Exception as e:

        print(f'{e=}')

        print('Reading with tifffile')
        # Read tiff file
        # ---------------------------------------------------------------------
        tiff = tf.imread(tiff_src)
        # ---------------------------------------------------------------------

        # Raise assertion to check that x and y are equal length
        # ---------------------------------------------------------------------
        assert tiff.shape[-1] == tiff.shape[-2]
        # ---------------------------------------------------------------------

        if num_z == 'None':
            num_z = None

        # Checks if tiff is read normally
        # ---------------------------------------------------------------------
        if len(tiff.shape) == 4:

            # Checks if channels is meant to be 4
            # assert tiff.shape[1]==4
            assert tiff.shape[1] == float(num_wav)

            return tiff
        # ---------------------------------------------------------------------

        elif num_z != None and len(tiff.shape) == 3:
            tiff_new_dim = tiff[np.newaxis, ...]
            return tiff_new_dim

        # Checks if tiff is (channels*z stacks, 2048, 2048)
        # ---------------------------------------------------------------------
        elif len(tiff.shape) == 3:

            # Define the variables needed
            # ---------------------------------------------------------------------
            num_of_wavelengths = int(float(num_wav))

            total_channels_times_z_stacks = tiff.shape[0]

            num_of_z = total_channels_times_z_stacks / num_of_wavelengths

            assert num_of_z == int(num_of_z), "The tiff file is not organized correctly."

            num_of_z = int(num_of_z)
            # ---------------------------------------------------------------------

            reshaped_tiff = tiff.reshape(num_of_z, num_of_wavelengths, tiff.shape[1], tiff.shape[2], order='F')
            # ---------------------------------------------------------------------

            return reshaped_tiff

        else:
            raise Exception("The tiff shape is weird!!!!!!!!")

    print('Shape after loading tiff:', str(tiff.shape))
    return tiff


if __name__ == '__main__':

    if sys.argv[1] == 'debug_load_tiff':
        tiff_src = '/groups/CaiLab/personal/Lex/raw/20k_dash_062421_brain/segmentation/MMStack_Pos0.ome.tif'
        num_wav = 2
        num_z = 1

        tiff = load(tiff_src, num_wav, num_z)

        print(f'{tiff.shape=}')

    if sys.argv[1] == 'debug_load_tiff_takei':
        tiff_src = '/groups/CaiLab/personal/Yodai/raw/2021-03-30-E14-100k-DNAfull-rep2-laminB1-H3K27me3-DAPI-H4K20me3/HybCycle_0/MMStack_Pos0.ome.tif'
        num_wav = 4
        num_z = None

        tiff = load(tiff_src, num_wav, num_z)

        print(f'{tiff.shape=}')
