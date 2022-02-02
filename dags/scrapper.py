# Source: https://www.astronomer.io/guides/dynamically-generating-dags

import sys
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import json
import logging
from datetime import datetime, timedelta
from libs import ec2, kinesis, role, dynamodb

logger = logging.getLogger(__name__)
dag_prefix_name="scrapper_"

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def create_dag(dag_id,
               schedule,
               dag_name,
               default_args):

    """
    Retrieves EC2 instance data assuming a role and pushes the records to Kinesis.
    """
    def push_data(*args):
        try:
            assumerole = role.AssumeRole(role_arn='arn:aws:iam::'+dag_name+':role/realtime-costs-client')
            session = assumerole.assumed_role_session()
            run = ec2.EC2(account_id=dag_name, session=session)
            run.get_instances_description_all()

            config = dynamodb.DynamoDB()

            stream = kinesis.KinesisStream(name=config.get_config('kinesis_ec2'))
            for i in run.description_list:
                stream.put_record(json.dumps(i, cls=DatetimeEncoder),i["AccountId"])

        except Exception as e:
            logging.error(e)
            sys.exit(1)

    dag = DAG(dag_id,
              schedule_interval=schedule,
              max_active_runs=1,
              is_paused_upon_creation=False,
              catchup=False,
              dagrun_timeout=timedelta(seconds=120),
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='push_data',
            python_callable=push_data)

        t1

    return dag

# Start
accounts = dynamodb.DynamoDB()
paginator = accounts.get_subscribed_accounts()

for page in paginator:
    for item in page['Items']:
        account_id = item['account_id']['S']
        
        dag_id = dag_prefix_name + account_id

        enabled_dags = [] # dynamic enabled_dags

        default_args = {'owner': 'airflow',
                        'start_date': datetime(2021, 1, 1),
                        'retries': 5,
                        'retry_delay': timedelta(minutes=2),
                    }

        schedule = '* * * * *'
        dag_name = account_id
        globals()[dag_id] = create_dag(dag_id,
                                    schedule,
                                    dag_name,
                                    default_args)     
