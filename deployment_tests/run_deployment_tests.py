import json
import os
import shutil
import filecmp
import sys

from helpers.make_new_test import insert_test

main_dir = os.environ['DATA_PIPELINE_MAIN_DIR']



#Set up Tests
#=======================================================================================================
#=======================================================================================================
experiment_name = 'test1'


#Test for decoding
#------------------------------------
decoding = { 'personal': 'nrezaee', 

              "experiment_name": experiment_name,
              
              "alignment": "no align",
              
              "alignment errors": "true",
              
              "dot detection": "top 1000 dots",
              
              "decoding": "across", 
              
              "allowed_diff":"0"
            }
            
insert_test(decoding, 'deployment_tests')            
#------------------------------------
#=======================================================================================================
#=======================================================================================================
#End of setting up tests



#Runs the Tests
#--------------------------------------------------------------------------------------
os.system('sh run_cron.sh /home/nrezaee/json_analyses')
#--------------------------------------------------------------------------------------



#Checks if the tests worked
#=======================================================================================================
#=======================================================================================================
#Checks if No align Test Worked
#--------------------------------------------------------------------------------------
if filecmp.cmp(main_dir + '/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/offsets.json', \
               '/home/nrezaee/test_cronjob/deployment_tests/results/no_align/offsets.json'):
    print("|| No align test                 || Passed!")
    
else: 
    print("|| No align test                 || Failed!")
#--------------------------------------------------------------------------------------


#Checks if Dot detection Test Worked
#--------------------------------------------------------------------------------------
where_locations_mat_should_be = main_dir+ '/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/Dot_Locations/locations.mat'

if os.path.isfile(where_locations_mat_should_be):
    print("|| Dot detection test            || Passed!")
else:
    print("|| Dot detection test            || Failed!")
#--------------------------------------------------------------------------------------


#Checks if Decoding Test Worked
#--------------------------------------------------------------------------------------
#Declare where files should be
#--------------------------------
where_finalPosList_mat_should_be = main_dir + '/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/Decoded/finalPosList.mat'
where_PosList_mat_should_be = main_dir +'/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/Decoded/PosList.mat'
where_seeds_mat_should_be = main_dir+'/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/Decoded/seeds.mat'
where_barcode_mat_should_be = main_dir+'/analyses/nrezaee/'+experiment_name+'/deployment_tests/BarcodeKey/barcode.mat'
#--------------------------------

#Check to see if files exist
#--------------------------------
if os.path.isfile(where_finalPosList_mat_should_be) and  \
   os.path.isfile(where_PosList_mat_should_be) and  \
   os.path.isfile(where_seeds_mat_should_be) and  \
   os.path.isfile(where_barcode_mat_should_be):

    print("|| Decoding test                 || Passed!")
else:
    print("|| Decoding test                 || Failed!")
#--------------------------------
#--------------------------------------------------------------------------------------
    

#Checks if Alignmnet Errors Test
#--------------------------------------------------------------------------------------
if os.path.exists(main_dir+'/analyses/nrezaee/'+experiment_name+'/deployment_tests/MMStack_Pos0/errors_for_alignment.json'):
              
    print("|| Alignment errors test         || Passed!")
else:
    print("|| Alignment errors test         || Failed!")
#--------------------------------------------------------------------------------------


#Checks if locations has correct shape
#--------------------------------------------------------------------------------------
from scipy.io import loadmat

locations = loadmat(where_locations_mat_should_be)

if locations["locations"].shape == (12,2):
    print("|| Locations Shape test          || Passed!")
else:
    print("|| Locations Shape test          || Failed!")
#--------------------------------------------------------------------------------------
#=======================================================================================================
#=======================================================================================================
#End of Checking tests




    
    
    
    
    
    
    
    
    
