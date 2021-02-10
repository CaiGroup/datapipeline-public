
rclone sync onedrive_caltech:Analysis_Files/ /groups/CaiLab/json_analyses
rclone delete onedrive_caltech:Analysis_Files

export DATA_PIPELINE_MAIN_DIR='/groups/CaiLab'

cd /home/nrezaee/test_cronjob_multi_dot/
sh /home/nrezaee/test_cronjob_multi_dot/run_cron.sh /groups/CaiLab/json_analyses/
