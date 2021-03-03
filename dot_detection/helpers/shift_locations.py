import numpy as np


def shift_locations(locations, offset, tiff_src, bool_chromatic):
    
    if np.all(offset == [0, 0, 0]):
        
        #No Shifting :( 
        
        pass
    
    else:
        
        offset = np.array(offset)
        
        
        if bool_chromatic==True:
            
            split_tiff_src = tiff_src.split(os.sep)
        
            personal = split_tiff_src[4]
            
            experiment_name= split_tiff_src[6]
            
            chromatic_offsets_src = os.path.join('/groups/CaiLab/analyses', personal, experiment_name, \
                                    analysis_name, 'Chromatic_Abberation_Correction/chromatic_offsets.json')
                                    
            with open(chromatic_offsets_src) as json_file: 
                chromatic_offsets = np.array(json.load(json_file))
                
            #---------------------------------------------------------------------
            
            
            #Shift for chromatic abberation
            #---------------------------------------------------------------------
            key  = "Channel " +str(channel)
            
            if chromatic_offsets[key] != [0,0,0]:
                
                offset = offset + chromatic_offset
            #---------------------------------------------------------------------


    

    if len(offset) == 3:
        
        locations_offsetted = np.array([location + offset for location in locations])
        
    elif len(offset) ==2:
        
        offset = np.roll(offset, 1)
        print(f'{np.max(locations)=}')
        print(f'{np.min(locations)=}')
        
        print(f'{locations[-10:]=}')
        print(f'{offset=}')
        locations_offsetted = np.array([np.append(np.array(location[:2]) + offset, location[-1]) \
                                for location in locations])
        print(f'{locations_offsetted[-10:]=}')
        print(f'{np.max(locations_offsetted)=}')
        print(f'{np.min(locations_offsetted)=}')
        
    return locations_offsetted
