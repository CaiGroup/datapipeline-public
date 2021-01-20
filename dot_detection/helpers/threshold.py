import numpy as np

def apply_thresh(dot_analysis, threshold):
    index = 0
    indexes = []
    len_of_dot_analysis = len(dot_analysis[1])
    while (index < len_of_dot_analysis):
        if dot_analysis[1][index] <= threshold:

            dot_analysis[0] = np.delete(dot_analysis[0], index, axis =0)
            dot_analysis[1] = np.delete(dot_analysis[1], index)
            
            len_of_dot_analysis-=1
            
            assert len_of_dot_analysis == len(dot_analysis[1])
        
            index-=1

        indexes.append(index)
        index+=1
        

    return dot_analysis