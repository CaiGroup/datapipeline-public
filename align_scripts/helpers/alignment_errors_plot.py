import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_alignment_errors_plot(align_errors_src, dst):
    

    #Open align errors
    #------------------------------------------------
    with open(align_errors_src) as json_file:
        data = json.load(json_file)
    #------------------------------------------------
        
    #Get value from each key
    #------------------------------------------------
    values = []
    for key in data.keys():
        values.append(data[key])
    print(f'{values=}')
    values = np.array(values)
    
    #Remove No difference
    #------------------------------------------------
    bool_indices = values != 'No Difference 0% (Same as compared DAPI Image)'
    print(f'{bool_indices=}')
    values = values[bool_indices]
    
    labels = np.array(list(data.keys()))[bool_indices]
    #------------------------------------------------
    
    
    #Get each value as float
    #------------------------------------------------
    print(f'{values=}')
    float_values = [float(value.split('by ')[1].split('%')[0]) for value in values]
    #------------------------------------------------
    
    #Make Plot
    #------------------------------------------------
    plt.figure(figsize = (20,10))
    plt.title('Alignment Errors (Anything Below Zero is bad)', fontsize=30)
    plt.ylabel('Percentage Improved', fontsize=20)
    plt.bar(labels, float_values)
    plt.tick_params(axis='x', labelrotation = 90)
    #------------------------------------------------
    
    #Save Plot to dest
    #------------------------------------------------
    plt.savefig(dst)
    #------------------------------------------------
    
import sys

if sys.argv[1] == 'debug_align_errors_plot':
    align_errors_src = '/groups/CaiLab/analyses/nrezaee/test1/align_test2/MMStack_Pos0/align_errors.json'
    dst = 'foo/align_errors.png'
    get_alignment_errors_plot(align_errors_src, dst)
    print(f'{dst=}')