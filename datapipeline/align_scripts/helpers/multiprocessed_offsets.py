def organize_multiprocessed_offsets(return_dict):
    split_on = 'HybCycle'
    prev_keys = list(return_dict.keys())
    for key in prev_keys:
        #Get New Key
        #--------------------------------------------
        new_key = split_on + key.split(split_on)[1]
        #print(f'{new_key=}')
        #--------------------------------------------

        #Replace with new key
        #--------------------------------------------
        return_dict[new_key] = return_dict[key]
        del return_dict[key]
        #--------------------------------------------
        
    return return_dict