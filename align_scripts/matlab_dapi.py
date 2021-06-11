import tempfile
import os
from scipy.io import loadmat
import numpy as np
import sys
import pickle

sys.path.append(os.getcwd())

from load_tiff import tiffy
from align_scripts.helpers.saving_offset import save_offset
from align_scripts.align_errors import get_align_errors
from align_scripts.helpers.saving_align_errors import save_align_errors

def matlab_dapi(fixed_image_src, moving_image_src, num_wav, rand_dir):

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
    
    #Save Offset
    #------------------------------------------------------------------
    save_offset(moving_image_src, offset, rand_dir)
    #------------------------------------------------------------------
    
    #Save Alignment Error
    #------------------------------------------------------------------
    fixed_tiff = tiffy.load(fixed_image_src, num_wav)
    moving_tiff = tiffy.load(moving_image_src, num_wav)
    
    align_error = get_align_errors(fixed_tiff, moving_tiff, offset)
    save_align_errors(moving_image_src, align_error, rand_dir)
    #------------------------------------------------------------------
    


if 'debug' not in sys.argv[1]:
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed_src")
    parser.add_argument("--moving_src")
    parser.add_argument("--rand_dir")
    parser.add_argument("--num_wav")
    
    args, unknown = parser.parse_known_args()
    
    matlab_dapi(args.fixed_src, args.moving_src, args.num_wav, args.rand_dir)

elif sys.argv[1] == 'debug_matlab_dapi':
    
    fixed_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_2/MMStack_Pos0.ome.tif'
    moving_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_4/MMStack_Pos0.ome.tif'
    
    rand_dir = 'foo/matlab_dapi'
    os.makedirs(rand_dir, exist_ok=True)
    num_wav = 4
    start_time = None
    
    matlab_dapi(fixed_src, moving_src, num_wav, rand_dir)
    