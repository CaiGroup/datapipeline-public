# import matplotlib.pyplot as plt
# import matplotlib.patheffects as path_effects
# import time
# import datetime
# import logging
# import numpy as np

# #Set Functions for Logging
# #--------------------------------------------------------------------
# def start_logging(logging_path):
#     #Start Logging with Date
#     #--------------------------------------------
#     start_time = time.time()
#     logging.basicConfig(filename=logging_path, level='INFO')
#     now = datetime.datetime.now()
#     start_message = "Starting Dating " +str(now)
#     logging.info(start_message)
#     #--------------------------------------------

#     return start_time

# def logg_elapsed_time(start_time, message):
#     current_time = time.time()

#     diff = str(round(((current_time- start_time)/60), 2))
#     full_message = diff + ' minutes passed ' + message
#     logging.info(full_message)

# #--------------------------------------------------------------------


# #Make and Save plot for logging
# #--------------------------------------------------------------------
# def save_time_plot(logging_src, plot_dst):
#     with open(logging_src, "r") as f:
#         logs = f.read()

#     log_list = logs.split('\n')[1:-1]
#     log_list_sep_colon = []
#     for elem in log_list:
#         log_list_sep_colon.append(elem.split(':')[2])

#     log_list_numbers = []
#     for elem in log_list_sep_colon:
#         log_list_numbers.append(float(elem.split(' ')[0]))

#     times = np.reshape(np.array(log_list_numbers), (-1,2))

#     start_times = times[:,0]
#     end_times = times[:,1]

#     labels = []
#     for elem in log_list_sep_colon[::2]:
#         labels.append(elem.split('Starting ')[1])

#     #Make Bar Chart
#     #------------------------------------------------------------
#     plt.figure(figsize=(20, 12))
#     x_points = range(len(end_times))
#     plt.barh(x_points, end_times, left = start_times)
#     #------------------------------------------------------------

#     #Plot Line
#     #------------------------------------------------------------
#     plt.plot(end_times, x_points, color='red', linewidth=4, \
#         path_effects=[path_effects.SimpleLineShadow(shadow_color="red", linewidth=5),path_effects.Normal()])
#     #------------------------------------------------------------


#     #Add Labels
#     #------------------------------------------------------------
#     plt.title('Analysis of Processing Time', fontsize=50)
#     plt.yticks(x_points, labels, fontsize=20)
#     plt.xticks(fontsize=20)
#     plt.xlabel('Minutes', fontsize=30)
#     plt.legend(prop={'size': 30})
#     #------------------------------------------------------------
#     plt.savefig(plot_dst)
# #--------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import time
import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import numpy as np

# Get the unique logger object for this file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set a single global log file name
GLOBAL_LOG_PATH = Path('/groups/CaiLab/analyses/pipeline_rotating_log_lincoln.txt')
# Set up a Handler that maxes out at ~1 MB
global_handler = RotatingFileHandler(GLOBAL_LOG_PATH, maxBytes=2**20, backupCount=1)
global_handler.setLevel(logging.INFO)

logger.addHandler(global_handler)


#Set Functions for Logging
#--------------------------------------------------------------------
def start_logging(logging_path):
    #Start Logging with Date
    #--------------------------------------------
    start_time = time.time()

    # configure the handler to write the log file in logging_path
    # (the normal location, in each analysis directory)
    local_handler = logging.FileHandler(logging_path)
    local_handler.setLevel(logging.INFO)

    # get the parent directory of the logging_path
    logging_parent = str(Path(logging_path).parent)

    # configure the formatters for the local and global logger
    format_string = '[%(asctime)s] %(levelname)s: %(message)s'

    local_formatter = logging.Formatter(format_string)
    local_handler.setFormatter(local_formatter)

    # The global logger includes the folder path in the message
    global_formatter = logging.Formatter(f'{logging_parent} : {format_string}')
    global_handler.setFormatter(global_formatter)

    # Add the local handler to the logger; the global handler is already added
    # at the top of this file.
    logger.addHandler(local_handler)

    now = datetime.datetime.now()
    start_message = "Starting logging " +str(now)
    logger.info(start_message)
    #--------------------------------------------

    return start_time

def logg_elapsed_time(start_time, message):
    current_time = time.time()

    diff = str(round(((current_time- start_time)/60), 2))
    full_message = diff + ' minutes passed ' + message
    logger.info(full_message)

#--------------------------------------------------------------------


#Make and Save plot for logging
#--------------------------------------------------------------------
def save_time_plot(logging_src, plot_dst):
    with open(logging_src, "r") as f:
        logs = f.read()

    log_list = logs.split('\n')[1:-1]
    log_list_sep_colon = []
    for elem in log_list:
        log_list_sep_colon.append(elem.split(':')[2])

    log_list_numbers = []
    for elem in log_list_sep_colon:
        log_list_numbers.append(float(elem.split(' ')[0]))

    times = np.reshape(np.array(log_list_numbers), (-1,2))

    start_times = times[:,0]
    end_times = times[:,1]

    labels = []
    for elem in log_list_sep_colon[::2]:
        labels.append(elem.split('Starting ')[1])

    #Make Bar Chart
    #------------------------------------------------------------
    plt.figure(figsize=(20, 12))
    x_points = range(len(end_times))
    plt.barh(x_points, end_times, left = start_times)
    #------------------------------------------------------------

    #Plot Line
    #------------------------------------------------------------
    plt.plot(end_times, x_points, color='red', linewidth=4, \
        path_effects=[path_effects.SimpleLineShadow(shadow_color="red", linewidth=5),path_effects.Normal()])
    #------------------------------------------------------------


    #Add Labels
    #------------------------------------------------------------
    plt.title('Analysis of Processing Time', fontsize=50)
    plt.yticks(x_points, labels, fontsize=20)
    plt.xticks(fontsize=20)
    plt.xlabel('Minutes', fontsize=30)
    plt.legend(prop={'size': 30})
    #------------------------------------------------------------
    plt.savefig(plot_dst)
#--------------------------------------------------------------------
