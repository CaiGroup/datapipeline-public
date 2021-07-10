import numpy as np



def combine_multiprocessed_points(return_dict):
    hyb_dirs = list(return_dict.keys())

    #Get Sorted Hyb List
    #===============================================================================
    #Split hybs to get numbers
    #-------------------------------------------------
    split_word_before = 'Cycle_'
    split_word_after = '/MMStack_Pos'
    for index in range(len(hyb_dirs)):

        hyb_dirs[index] = hyb_dirs[index].split(split_word_before)
        hyb_dirs[index][1] = hyb_dirs[index][1].split(split_word_after)

        #hyb_dirs[index] = [inner for outer in hyb_dirs[index] for inner in outer]

        temp = hyb_dirs[index][1]
        hyb_dirs[index][1] = temp[0]
        hyb_dirs[index].append(temp[1])

        #print(f'{hyb_dirs[index]=}')
        hyb_dirs[index][1] = int(hyb_dirs[index][1])
    #-------------------------------------------------


    #Sort the Hybs
    #-------------------------------------------------
    sorted_hyb_dirs = sorted(hyb_dirs, key=lambda x: x[1])
    #print(f'{sorted_hyb_dirs=}')
    #-------------------------------------------------


    #Combine the strings to right format
    #-------------------------------------------------
    for index in range(len(sorted_hyb_dirs)):
        sorted_hyb_dirs[index][1] = str(sorted_hyb_dirs[index][1])

        sorted_hyb_dirs[index].insert(1, split_word_before)
        sorted_hyb_dirs[index].insert(3, split_word_after)
        #print(f'{sorted_hyb_dirs[index]=}')
        sorted_hyb_dirs[index] = ''.join(sorted_hyb_dirs[index])
    #-------------------------------------------------
    #===============================================================================
    
    #Combine the dots in tiff
    #-------------------------------------------------
    locations = []
    check_if_first_tiff = 0
    for key in sorted_hyb_dirs:
        #print(f'{check_if_first_tiff=}')
        if check_if_first_tiff == 0:
            locations = return_dict[key]
            

            check_if_first_tiff +=1
        else:

            for location in return_dict[key]:
                assert location != None
                locations.append(location)
    #-------------------------------------------------
    
    #print(f'{len(locations)=}')
    return locations
