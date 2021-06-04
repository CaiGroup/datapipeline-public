import os
import json
import re

def get_specific_positions(spec_positions, positions):
    """
    Inputs:
        spec_postions: list of numbers
        positions: list of MMStack_Pos{n}.ome.tif's
    Outpus:
        list of MMStack_Pos{n}.ome.tif's in spec_positions
    """
    
    
    #Split positions to get position numbers
    positions_split = [re.split('Pos|,|.ome.tif', position) 
                       for position in positions]
    
    #Check if position number in .ome.tif's and add to list
    spec_positions_split = []
    for spec_position in spec_positions:
        for position_split in positions_split:
            if spec_position in position_split:
                print(f'{position_split=}')
                spec_positions_split.append(position_split)
    
    #Combine splitted positions
    result_positions = [spec_position_split[0] + 'Pos' + spec_position_split[1] \
                    + '.ome.tif' for spec_position_split in spec_positions_split]
    
    return result_positions
    

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
    
def get_positions_in_data(data, main_dir):
    """
    Check to see if "positions" are in json
    If "positions" are in json, then get specific positions
    """

    #Get single position
    #----------------------------------------------------------
    if 'decoding with previous locations variable' in data.keys():
        if data['decoding with previous locations variable'] == 'true':
            
            positions = ['MMStack_Pos0.ome.tif']

    else:
        
        #Get all positions
        #-----------------------------
        exp_dir = os.path.join(main_dir, "personal", data["personal"], "raw", data["experiment_name"])
        hybs = [hyb for hyb in os.listdir(exp_dir) if 'Hyb' in hyb]
        path_to_sub_dir = os.path.join(exp_dir, hybs[0])
        positions = os.listdir(path_to_sub_dir)
        #-----------------------------
        
        #Check if "positions" in json
        if 'positions' in data.keys():
            if data['positions'] != 'none':
                if hasNumbers(data['positions']):
                    #Get Specific Positions
                    positions = get_specific_positions(data['positions'], positions)
                        
        print(2)

    return positions
    
  
# Opening JSON file
with open('/home/nrezaee/test_analyses/2021-03-30-E14-100k-DNAfull-rep2-test1.json') as json_file:
    data = json.load(json_file)
    
result_positions = get_positions_in_data(data, '/groups/CaiLab')
print(f'{result_positions=}')

