# Data Pipeline
How to analyze data with a simple json upload!

## Simple Explanation
![Simple Explanation](https://github.com/CaiGroup/data-pipeline/blob/master/docs/images/simple_explanation%20(3).png)

## Comprehensive Explanation
![Comprehensive Explanation](https://github.com/CaiGroup/data-pipeline/blob/master/docs/images/comprehensive%20explanation%20(1).png)

## Tutorial Video
Go the the link below to download the mp4 file of the tutorial video.

"https://github.com/CaiGroup/data-pipeline/blob/master/docs/Tutorial%20Video/analysis_tutorial.mp4"


## Setting up a DEV environment to add New Feature 

1. Enter your home directory on the Caltech HPC

2. Clone the data-pipeline repository:
   **git clone https://github.com/CaiGroup/data-pipeline**
   
3. Make your json source directory
   **mkdir ~/json_analyses**

4. Enter the cloned repo
   **cd data-pipeline**
   
5. Run the pipeline with **~/json_analyses** as the json source directory
   **sh run_cron.sh /home/{username}/json_analyses/**
   
6. Now you can add your feature to the code and test it out in your DEV pipeline

7. Create a pull request for approval to add your feature to the pipeline in production
