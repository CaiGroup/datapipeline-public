alias awsw='aws s3 --endpoint-url=https://s3.us-west-1.wasabisys.com --profile hpc-wasabi-user --region us-west-1'

awsw sync s3://hpc-wasabi/json_analyses /groups/CaiLab/json_analyses
awsw rm s3://hpc-wasabi/json_analyses --recursive
