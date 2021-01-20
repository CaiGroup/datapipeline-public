import os
import pandas as pd
import tempfile

def combine_barcodes(barcode_src1, barcode_src2):
    
    barcode1 = pd.read_csv(barcode_src1)
    barcode2 = pd.read_csv(barcode_src2)
    
    combined_barcodes = barcode1.append(barcode2).reset_index(drop=True)
    
    #combined_barcodes = combined_barcodes[combined_barcodes.columns[1:]]
    
    return combined_barcodes 

def read_barcode(barcode_src, barcode_dst, bool_fake_barcodes): 
    
    #Get Current working directory
    #------------------------------------------------------------------
    cwd = os.getcwd()
    
    cwd = cwd[cwd.find('/home'):]

    read_barcode_dir = os.path.join(cwd, 'read_barcode')
    
    print(f'{read_barcode_dir=}')
    #------------------------------------------------------------------
    
    
    #Fake Barcodes
    #------------------------------------------------------------------
    if bool_fake_barcodes == True:
        
        #------------------------------------------------------------------
        barcode_key_dir = os.path.dirname(barcode_src)
        
        fake_barcodes_path = os.path.join(barcode_key_dir, 'fake_barcode.csv')
        #------------------------------------------------------------------
        
        
        #------------------------------------------------------------------
        df_combined_barcodes = combine_barcodes(barcode_src, fake_barcodes_path) 
        
        temp_dir = tempfile.TemporaryDirectory()
        
        comb_barcode_dst = os.path.join(temp_dir.name, 'combined_barcode.csv')
        
        df_combined_barcodes.to_csv(comb_barcode_dst, index=False)
        #df_combined_barcodes.to_csv('test.csv')
        
        print(f'{comb_barcode_dst=}')
        
        barcode_src = comb_barcode_dst
        #------------------------------------------------------------------
        
        
    #----------------------------------------------------------------
    
    #Creating Matlab Command
    #------------------------------------------------------------------
    
    print(f'{barcode_src=}')
    
    assert os.path.isfile(barcode_src) == True
    
    cmd = """  matlab -r "addpath('{2}'); readbarcode( '{0}' , '{1}', 'header'); quit"; """ 

    cmd = cmd.format(barcode_src, barcode_dst, read_barcode_dir)
    #------------------------------------------------------------------

    #Running Matlab Command
    #------------------------------------------------------------------
    print("Running Matlab Command for reading barcodes:", cmd, flush=True)
    
    print(f'{barcode_src=}')    

    os.system(cmd)
    #------------------------------------------------------------------
    
    return None
    
