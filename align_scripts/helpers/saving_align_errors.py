import pickle
import os


def save_align_errors(moving_image_src, error, rand_dir):
    pos = moving_image_src.split(os.sep)[-1]
    hyb = moving_image_src.split(os.sep)[-2]
    
    dest = os.path.join(rand_dir, 'align_error_' + hyb + '_______' + pos + '.pkl')
    print(f'{dest=}')
    
    with open(dest, 'wb') as filehandle:
    # store the data as binary data stream
        pickle.dump(error, filehandle)
