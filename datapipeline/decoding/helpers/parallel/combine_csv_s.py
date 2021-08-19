import pandas as pd
import glob
import os


def get_combined_csv(dest, rand_list, dest_unfilt, dest_filt):
    
    #Get the Actual CSV's 
    #-------------------------------------------------
    all_unfilt_csv_s = []
    all_filt_csv_s = []
    for rand in rand_list:
        glob_me_filt = os.path.join(dest, rand, '*unfiltered.csv')
        glob_me_unfilt = os.path.join(dest, rand, '*_filtered.csv')
        
        unfiltered_csv_s = glob.glob(glob_me_unfilt)
        filtered_csv_s = glob.glob(glob_me_filt)
        
        print(f'{rand=}')

        
        assert len(unfiltered_csv_s) != 0, 'Something messed up in the decoding'
        
        if len(unfiltered_csv_s) == 1:
         
            all_unfilt_csv_s.append(unfiltered_csv_s[0])
            all_filt_csv_s.append(filtered_csv_s[0])
        else:
            print('bye')
            
    #Combine the CSV's into one
    #-------------------------------------------------
    df_comb_unfilt = pd.read_csv(all_unfilt_csv_s[0])
    
    for csv in all_unfilt_csv_s[1:]:
        
        df_comb_me = pd.read_csv(csv)
        
        
        df_comb_unfilt = df_comb_unfilt.append(df_comb_me, ignore_index=True)
        #print(f'{df_comb.shape=}')
    #-------------------------------------------------
    
    #Combine the CSV's into one
    #-------------------------------------------------
    df_comb_filt = pd.read_csv(all_filt_csv_s[0])
    
    for csv in all_filt_csv_s[1:]:
        
        df_comb_me = pd.read_csv(csv)
        print(f'{df_comb_me.shape=}')
        
        
        df_comb_filt = df_comb_filt.append(df_comb_me, ignore_index=True)
    
    #-------------------------------------------------
    
    #Save Combined Dataframe
    #-------------------------------------------------
    print(f'{df_comb_unfilt.shape=}')
    df_comb_unfilt.to_csv(dest_unfilt, index = False)
    #-------------------------------------------------
    
    #Save Combined Dataframe
    #-------------------------------------------------
    print(f'{df_comb_filt.shape=}')
    df_comb_filt.to_csv(dest_filt, index = False)
    #-------------------------------------------------
    
    return None
