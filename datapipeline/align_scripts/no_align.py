import numpy as np
import os
import pickle

def no_align(fixed_image_src, moving_image_src, rand_dir):
    
    offset = [0,0,0]
    
    pos = moving_image_src.split(os.sep)[-1]
    hyb = moving_image_src.split(os.sep)[-2]
    
    dest = os.path.join(rand_dir, hyb + '_______' + pos + '.pkl')
    print(f'{dest=}')
    with open(dest, 'wb') as filehandle:
        pickle.dump(offset, filehandle)
    
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--fixed_src")
parser.add_argument("--moving_src")
parser.add_argument("--rand_dir")

args, unknown = parser.parse_known_args()

no_align(args.fixed_src, args.moving_src, args.rand_dir)


















