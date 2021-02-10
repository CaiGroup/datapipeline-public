import pickle
import os
from scipy.io import savemat


def combine_locs(rand_list):
    check_if_first_tiff = 0
    temp_dir = '/groups/CaiLab/personal/nrezaee/temp_dots'
    for rand in rand_list:
        print(temp_dir, rand)
        locs_src = os.path.join(temp_dir, rand, 'locs.pkl')
        
            
        with open(locs_src, 'rb') as f:
            dots_in_tiff = pickle.load(f)
    
        if check_if_first_tiff == 0:
            locations = dots_in_tiff
            print(f'{len(locations)=}')
                
            check_if_first_tiff +=1
        else:

            for location in dots_in_tiff:
                assert location != None
                locations.append(location)
                print(f'{len(locations)=}')
                
    return locations
                
    
    
# rand_list = ['8iuWI5BK',  'KKkCNppu',  'Qd1MJQNU', 'tIV32ilp']

# combine_locs(rand_list)