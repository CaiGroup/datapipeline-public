import glob
import os
import pickle

def combine_offsets(rand_list):
    
    temp_dir = '/groups/CaiLab/personal/temp/temp_align'
    offsets = {}
    
    for rand in rand_list:
        
        #Check for Hyb* in directory
        #---------------------------------------------
        glob_rand_dir = os.path.join(temp_dir, rand, 'Hyb*')
        
        print(f'{glob_rand_dir=}')
        
        off_pkls = glob.glob(glob_rand_dir)
        #---------------------------------------------
        
        #Check to see if background instead of hyb
        #---------------------------------------------
        if len(off_pkls) == 0:
            glob_rand_dir = os.path.join(temp_dir, rand, 'final_background*')
            print(f'{glob_rand_dir=}')
            off_pkls = glob.glob(glob_rand_dir)
            assert len(off_pkls) == 1, "Aligning the final background messed up"
            off_pkl = off_pkls[0]
        #---------------------------------------------
        
        #It is a hyb or error
        #---------------------------------------------
        elif len(off_pkls) == 1:
            off_pkl = glob.glob(glob_rand_dir)[0]
        else:
            raise Exception(' There is more than one .pkl for offset')
        #---------------------------------------------
            
        #Get offset from pickle
        #---------------------------------------------
        with open(off_pkl, 'rb') as fp:
            offset = pickle.load(fp)
        #---------------------------------------------
    
        #Save Offset
        #---------------------------------------------
        hyb_pos = off_pkl.split(os.sep)[-1]
        
        hyb = hyb_pos.split('_______')[0]
        pos = hyb_pos.split('_______')[1].replace('.pkl', '')
        
        key = os.path.join(hyb, pos)
        
        offsets[key] = offset
        #---------------------------------------------
        
      
    return offsets

def combine_align_errors(rand_list):
    
    temp_dir = '/groups/CaiLab/personal/temp/temp_align'
    offsets = {}
    
    for rand in rand_list:
        glob_rand_dir = os.path.join(temp_dir, rand, 'align_error_*')
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

if __name__ == '__main__':

    import sys
    if sys.argv[1] == 'debug_combine_align':
        rand_list = ['DnoWCMPA', 'kB9q7SuX', 'kgrbUmx9', 'wXBkepqw']
        combine_offsets(rand_list)
    
    