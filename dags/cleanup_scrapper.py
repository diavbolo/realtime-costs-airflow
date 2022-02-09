# https://github.com/teamclairvoyant/airflow-maintenance-dags/blob/master/clear-missing-dags/airflow-clear-missing-dags.py
from airflow.models import DAG, DagModel
from airflow.operators.python_operator import PythonOperator
from airflow import settings
from datetime import datetime, timedelta
import os
import logging

dag_prefix_name ="scrapper_"

dag_id=os.path.basename(__file__).replace(".py", ""),
schedule = '*/5 * * * *'
default_args = {'owner': 'airflow',
                'start_date': datetime(2021, 1, 1),
                'retries': 3,
                'retry_delay': timedelta(minutes=5),
                }

"""
Delete DAGs for unsubscribed AWS accounts
"""
def cleanup_scrapper(*args):

    from libs import dynamodb

    logger = logging.getLogger(__name__)

    session = settings.Session()
    
    accounts = dynamodb.DynamoDB()
    paginator = accounts.get_unsubscribed_accounts()

    for page in paginator:
        for item in page['Items']:
            dag_name = dag_prefix_name + item['account_id']['S']
            query = session.query(DagModel).filter(DagModel.dag_id == dag_name)
            logging.info('Deleting DAG ' + dag_name)
            query.delete(synchronize_session=False)

    session.commit()

with DAG(
    dag_id=os.path.basename(__file__).replace(".py", ""),
    schedule_interval=schedule,
    max_active_runs=1,
    is_paused_upon_creation=False,
    catchup=False,
    default_args=default_args
) as dag:
    t1 = PythonOperator(
    task_id='cleanup_scrapper',
    python_callable=cleanup_scrapper)

    t1