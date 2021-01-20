import tempfile
import os
from scipy.io import loadmat
import numpy as np
import sys
import pickle

sys.path.append(os.getcwd())

from load_tiff import tiffy
from align_scripts.helpers.saving_offset import save_offset

def matlab_dapi(fixed_image_src, moving_image_src, rand_dir):

    #Create Dest
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    dest = os.path.join(temp_dir.name, 'offset')
    #-------------------------------------------------------------------
    
    #Create Paths to add
    #-------------------------------------------------------------------
    cwd = os.getcwd()
    
    cwd = cwd[cwd.find('/home'):]

    matlab_dapi_dir = os.path.join(cwd, 'align_scripts','matlab_dapi')
    
    bfmatlab_dir = os.path.join(matlab_dapi_dir, 'bfmatlab')
    #-------------------------------------------------------------------
    
    
    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    cmd = """  matlab -r "addpath('{0}');addpath('{1}');full_wrap_alignment('{2}', '{3}', '{4}'); quit"; """ 
    
    cmd = cmd.format(matlab_dapi_dir, bfmatlab_dir, fixed_image_src, moving_image_src, dest)
    
    os.system(cmd)
    #-------------------------------------------------------------------
    
    
    print(f'{os.listdir(temp_dir.name)=}')
    
    #Get offset from mat file 
    #------------------------------------------------------------------
    f = open(dest+'.txt', "r")
    offset = f.read()
    temp_dir.cleanup()
    

    offset = offset.split(',')
    offset = [round(float(off),5) for off in offset ]
    
    if offset[2] ==0:
        offset.pop()
    #------------------------------------------------------------------
    
    save_offset(moving_image_src, offset, rand_dir)
    



import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--fixed_src")
parser.add_argument("--moving_src")
parser.add_argument("--rand_dir")

args, unknown = parser.parse_known_args()

matlab_dapi(args.fixed_src, args.moving_src, args.rand_dir)