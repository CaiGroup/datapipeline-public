aws s3 sync s3://flask-web-test/json_analyses /groups/CaiLab/json_analyses
sh /home/nrezaee/test_cronjob_multi_dot/run_cron.sh /groups/CaiLab/json_analyses
aws s3 rm s3://flask-web-test/json_analyses --recursive
