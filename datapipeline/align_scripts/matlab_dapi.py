import tempfile
import os
from scipy.io import loadmat, savemat
import numpy as np
import sys


from webfish_tools.util import pil_imread
#from align_errors import get_align_errors

def matlab_dapi(fixed_image_src, moving_image_src, dest_folder):

    #Create Dest
    #-------------------------------------------------------------------
    os.makedirs(dest_folder, exist_ok=True)
    #-------------------------------------------------------------------

    cwd = os.path.dirname(__file__)
    #cwd = cwd[cwd.find('/home'):]

    matlab_dapi_dir = os.path.join(cwd, 'matlab_dapi')
    bfmatlab_dir = os.path.join(matlab_dapi_dir, 'bfmatlab')
    #-------------------------------------------------------------------

    #Open tiff files and get DAPI Channel
    #-------------------------------------------------------------------
    fixed_tiff = pil_imread(fixed_image_src)
    moving_tiff = pil_imread(moving_image_src)
    print(f'{fixed_tiff.shape=}')
    print(f'{moving_tiff.shape=}')

    fixed_dapi = fixed_tiff[-1]
    moving_dapi = moving_tiff[-1]
    #-------------------------------------------------------------------

    #Save dapi's to mat file
    #-------------------------------------------------------------------
    mat_dst = os.path.join(dest_folder, 'dapi_s.mat')
    savemat(mat_dst, {'fixed_dapi': fixed_dapi, 'moving_dapi': moving_dapi})
    #-------------------------------------------------------------------

    print(f'{os.getcwd()=}')
    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    dest_file = os.path.join(dest_folder, 'offset')
    cmd = """  matlab -r "addpath('{0}');addpath('{1}');full_wrap_alignment('{2}', '{3}'); quit"; """

    cmd = cmd.format(matlab_dapi_dir, bfmatlab_dir, mat_dst, dest_file)

    os.system(cmd)
    #-------------------------------------------------------------------

    dest_file = dest_file + '.txt'
    offset = open(dest_file, 'r').read().split(',')
    offset = [float(o) for o in offset[:2]]

    #align_error = get_align_errors(fixed_tiff.swapaxes(0, 1), moving_tiff.swapaxes(0, 1), offset)
    #print(f'{offset=}')
    #------------------------------------------------------------------

if 'debug' not in sys.argv[1]:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed_src")
    parser.add_argument("--moving_src")
    parser.add_argument("--dest_dir")

    args, unknown = parser.parse_known_args()

    matlab_dapi(args.fixed_src, args.moving_src, args.dest_dir)


