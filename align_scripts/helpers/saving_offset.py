import pickle
import os


def save_offset(moving_image_src, offset, rand_dir):
    pos = moving_image_src.split(os.sep)[-1]
    hyb = moving_image_src.split(os.sep)[-2]
    
    dest = os.path.join(rand_dir, hyb + '_______' + pos + '.pkl')
    print(f'{dest=}')
    
    if type(offset) != list:
        offset = offset.tolist()
    
    with open(dest, 'wb') as filehandle:
    # store the data as binary data stream
        pickle.dump(offset, filehandle)
