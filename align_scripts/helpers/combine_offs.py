import glob
import os
import pickle

def combine_offsets(rand_list):
    
    temp_dir = '/groups/CaiLab/personal/nrezaee/temp_align'
    offsets = {}
    
    for rand in rand_list:
        glob_rand_dir = os.path.join(temp_dir, rand, 'Hyb*')
        print(f'{glob_rand_dir=}')
        
        off_pkl = glob.glob(glob_rand_dir)[0]

            
        with open(off_pkl, 'rb') as fp:
            offset = pickle.load(fp)
    
        #Save Offset
        #---------------------------------------------
        hyb_pos = off_pkl.split(os.sep)[-1]
        
        hyb = hyb_pos.split('_______')[0]
        pos = hyb_pos.split('_______')[1].replace('.pkl', '')
        
        key = os.path.join(hyb, pos)
        
        offsets[key] = offset
        #---------------------------------------------
        
      
    return offsets


# rand_list = ['DnoWCMPA', 'kB9q7SuX', 'kgrbUmx9', 'wXBkepqw']

# combine_offsets(rand_list)