import os
import pickle


def save_offset(moving_image_src, offset, rand_dir):
    print(moving_image_src, offset, rand_dir)
    # Make dest file
    # ------------------------------------------------
    pos = moving_image_src.split(os.sep)[-1]
    hyb = moving_image_src.split(os.sep)[-2]

    dest = os.path.join(rand_dir, str(hyb) + '_______' + str(pos) + '.pkl')
    print(f'{dest=}')
    # ------------------------------------------------

    # Turn into list object
    # ------------------------------------------------
    if type(offset) != list:
        offset = offset.tolist()
    # ------------------------------------------------

    # Dump into pickle
    # ------------------------------------------------
    with open(dest, 'wb') as filehandle:
        pickle.dump(offset, filehandle)
    # ------------------------------------------------
