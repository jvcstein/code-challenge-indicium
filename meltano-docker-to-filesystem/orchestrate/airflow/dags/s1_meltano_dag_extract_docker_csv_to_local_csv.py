from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),  # This defines when Airflow starts tracking
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's1_meltano_dag_extract_docker_csv_to_local_csv',
    default_args=default_args,
    description='Run meltano run tap-csv-docker target-csv-csv daily',
    schedule_interval='@daily',
    catchup=False
)

run_meltano = BashOperator(
    task_id='run_meltano',
    bash_command='START_DATE=$(date +%Y-%m-%d) meltano run tap-csv-docker target-csv-csv',
    dag=dag,
)

run_meltano
