import os
from scipy.io import loadmat

def colocalize(locations_src, dest):

    dirname = os.path.dirname(__file__)
    path2 = os.path.join(dirname, 'matlab')
    #Create Matlab Command
    #-------------------------------------------------------------------
    cmd = "matlab -r \"addpath('/" \
          + dirname \
          + "'); addpath('" \
          + path2 \
          + "'); main_coloc('{0}', '{1}', {2}); quit\"; "
  
    radius = 2
    
    cmd = cmd.format(locations_src, dest, radius)
    
    print("    Matlab Command for Colcalization:", cmd, flush=True)
    #-------------------------------------------------------------------
    
    #Run Matlab Command
    #-------------------------------------------------------------------
    os.system(cmd)
    #-------------------------------------------------------------------
    
    return None


#Test for Colocalization
#----------------------------------------------------
# locations_src = '/groups/CaiLab/analyses/nrezaee/2020-07-29-nrezaee-test1/dot/MMStack_Pos0/locations.mat'

# dest = 'nothing'

# colocalize(locations_src, dest)
#----------------------------------------------------






    