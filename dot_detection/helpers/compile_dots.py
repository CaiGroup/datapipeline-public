import numpy as np

def add_to_dots_in_channel(dots_in_channel, dot_analysis):
    #Define Dots in Channel
    #---------------------------------------------------------------------
    if dots_in_channel == None:
        if dot_analysis[0].shape != (0,3):

            dots_in_channel = dot_analysis
    #---------------------------------------------------------------------
    
    
    #Concatenate dots
    #---------------------------------------------------------------------
    else:
        dots_in_channel[0] = np.concatenate((dots_in_channel[0], dot_analysis[0])).tolist()
        dots_in_channel[1] = np.concatenate((dots_in_channel[1], dot_analysis[1])).tolist()
        #print(f'{len(dots_in_channel[0])=}')
    #---------------------------------------------------------------------
    
    return dots_in_channel
    