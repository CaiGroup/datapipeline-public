import tempfile
import os
from scipy.io import loadmat
import numpy as np

def get_matlab_dapi_alignment(fixed_src, moving_src):
        
        
    #Create Dest
    #-------------------------------------------------------------------
    temp_dir = tempfile.TemporaryDirectory()
    dest = os.path.join(temp_dir.name, 'offset')
    #-------------------------------------------------------------------
    

    #Create Matlab Command and Call it
    #-------------------------------------------------------------------
    cmd = """  matlab -r "full_wrap_alignment('{0}', '{1}','{2}'); quit"; """ 
    
    cmd = cmd.format(fixed_src, moving_src, dest)
    
    os.system(cmd)
    #-------------------------------------------------------------------
    
    
    print(f'{os.listdir(temp_dir.name)=}')
    
    #Get offset from mat file 
    #------------------------------------------------------------------
    f = open(dest+'.txt', "r")
    offset = f.read()
    temp_dir.cleanup()
    

    offset = offset.split(',')
    offset = [float(off) for off in offset ]
    
    #------------------------------------------------------------------
    

    return offset

fixed_src = 'fixed_small.tif'
moving_src = 'moving_small.tif'
offset = get_matlab_dapi_alignment(fixed_src, moving_src)
print(f'{offset=}')