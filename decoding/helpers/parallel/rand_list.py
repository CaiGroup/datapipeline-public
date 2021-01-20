import getpass
import subprocess
import string 
import random



def are_jobs_finished(job_names):
    
    #Get User and Output
    #---------------------------------
    user = getpass.getuser()
    slurm_out = str(subprocess.check_output(['squeue', '-u', user]))
    #---------------------------------

    
    #Check if Finished
    #---------------------------------
    if any(x in slurm_out for x in job_names):
        
        #print ("Jobs Not Finished")
        bool_jobs_finished = False
    else:
        #print ("Jobs Finished")
        bool_jobs_finished  = True
    #---------------------------------
    
    return bool_jobs_finished
    

def id_generator(size=8):
    rand_choices = string.ascii_letters + '1234567890'
    return ''.join(random.choice(rand_choices) for _ in range(size))
    
def get_random_list(N):
    rand_list = []
    for i in range(N):
        rand_list.append(id_generator())
    
    return rand_list