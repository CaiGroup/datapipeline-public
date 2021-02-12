import json
import pandas as pd

def delete_unneeded(data):
    data = {k: data[k] for k in data.keys() if 'step' not in k}
    del data['analysis form']
    del data['what post analyses?']
    del data['owner']
    del data['experiment']
    del data['']
    del data['sidenote: separate position numbers by comma - "1,2,5"']
    return data

def correct_bools(data):
    change_bools = ['radial center ', 'alignment errors', 'visualize dots', 'gaussian fitting', \
                    'nuclei cyto match', 'fake barcodes', 'on/off barcode plot', \
                    'false positive analysis', 'hamming analysis', 'cyto labeled image', \
                    'nuclei labeled image']
    
    for key in change_bools:
        if data[key] == 0:
            data[key] = "false"
            
    for key in change_bools:
        if data[key] == True:
            data[key] ='true'
            
    return data

def get_lowercase(analysis_dict):
    data = {}
    for key, value in analysis_dict.items():
        if type(value) == str:
            if key.lower() == 'personal' or key.lower() == 'experiment_name':
                data[key.lower()] = value
            else:
                data[key.lower()] = value.lower()
        else:
            data[key.lower()] = value
            
    return data

def change_false_to_0(data):
    
    change_me = ['edge deletion', 'distance between nuclei', 'nucleus erode',  \
                 'cyto erode', 'positions', 'cyto channel number']
    
    for key in change_me:
        if data[key] == 'False':
            data[key] = '0'
            
    return data

def get_dict_from_excel(excel_path):
    df = pd.read_excel(excel_path, keep_default_na =False)
    #print(df)
    data = dict(zip(df['Unnamed: 2'], df['Unnamed: 3']))

    
    data['experiment_name'] = data['Experiment']
    data['personal'] = data['Owner']
    
    data = get_lowercase(data)

    data = correct_bools(data)
    
    if 'number of rounds - 1' in data['minimum seeds']:
        data['minimum seeds'] = 'number of rounds - 1'
    
    if 'default' in data['allowed diff']:
        data['allowed diff'] = "1"
        
    for key in data.keys():
        if type(data[key]) != str:
            data[key] = str(data[key])
            
    data = change_false_to_0(data)
    
    data = delete_unneeded(data)

    return data