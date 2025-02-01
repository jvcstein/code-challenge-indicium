from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),  
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's2_meltano_dag_create_order_details_at_docker_postgresql',
    default_args=default_args,
    description='Run meltano run tap-csv-local target-postgres daily',
    schedule_interval=None,
    catchup=False
)

wait_for_s1_meltano_dag_extract_docker_postgresql_to_local_csv_dag = ExternalTaskSensor(
    task_id="wait_for_s1_meltano_dag_extract_docker_postgresql_to_local_csv_dag",
    external_dag_id="s1_meltano_dag_extract_docker_postgresql_to_local_csv",  
    external_task_id=None,  
    execution_date_fn=lambda dt: dt,
    mode="poke",
    poke_interval=5,
    timeout=600
)

wait_for_s1_meltano_dag_extract_docker_csv_to_local_csv_dag = ExternalTaskSensor(
    task_id="wait_for_s1_meltano_dag_extract_docker_csv_to_local_csv_dag",
    external_dag_id="s1_meltano_dag_extract_docker_csv_to_local_csv",  
    external_task_id=None,  
    execution_date_fn=lambda dt: dt,
    mode="poke",
    poke_interval=5,
    timeout=600
)

run_meltano = BashOperator(
    task_id='run_meltano',
    bash_command='START_DATE=$(date +%Y-%m-%d) meltano run tap-csv-local target-postgres',
    dag=dag,
)

[
    wait_for_s1_meltano_dag_extract_docker_postgresql_to_local_csv_dag, 
    wait_for_s1_meltano_dag_extract_docker_csv_to_local_csv_dag
] >> run_meltano
