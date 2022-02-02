# realtime-costs-airflow

## Description

This repository contains the MWAA DAGs to be deployed in order to scrape out the data from AWS accounts for EC2 instances. For more information see [here](https://github.com/diavbolo/realtime-costs)

It contains three DAGs:
1. scrapper.py: dynamic DAG that reads the subscriptions from DynamoDB and deploys a DAG for each of them
2. cleanup_scrapper.py: deletes the DAGs for unsubscribed customers also based on DynamoDB
3. cleanup_db.py: cleans old data in the MWAA DB

It is integrated via CI/CD based on the configuration established in [the main repository](https://github.com/diavbolo/realtime-costs) so any change will be automatically deployed


## Setup instructions

### Configure

1. Deploy [the main repository](https://github.com/diavbolo/realtime-costs)
2. `git clone` the current repository and create a new GitHub repository
3. Change [this line](https://github.com/diavbolo/realtime-costs-airflow/blob/master/buildspec.yml#L11) as configured in the main reposiroty so it points to your S3 DAG bucket
4. `git add+commit+push` the files to your new repository
