import getpass
import random
import string
import subprocess


def get_squeue_output():
    user = getpass.getuser()
    return subprocess.check_output(['squeue', '--Format=Name', '--me']).decode()


def are_jobs_finished(job_names):
    # Get User and Output
    # ---------------------------------
    user = getpass.getuser()
    slurm_out = str(subprocess.check_output(['squeue', '--Format=Name', '--me']))
    # ---------------------------------

    # Check if Finished
    # ---------------------------------
    if any(x in slurm_out for x in job_names):

        # print ("Jobs Not Finished")
        bool_jobs_finished = False
    else:
        # print ("Jobs Finished")
        bool_jobs_finished = True
    # ---------------------------------

    return bool_jobs_finished


def id_generator(size=20):
    rand_choices = string.ascii_letters + '1234567890'
    return ''.join(random.choice(rand_choices) for _ in range(size))


def get_random_list(N):
    rand_list = []
    for i in range(N):
        rand_list.append(id_generator())

    return rand_list
