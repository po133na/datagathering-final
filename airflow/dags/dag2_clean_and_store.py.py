from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append("/opt/airflow")

from src.job2_cleaner import run_cleaner


with DAG(
    dag_id="dag2_clean_and_store",
    start_date=datetime(2025, 12, 14),
    schedule_interval="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["weather", "batch", "kafka", "sqlite"],
) as dag:

    clean_and_store = PythonOperator(
        task_id="clean_kafka_and_store_sqlite",
        python_callable=run_cleaner,
        execution_timeout=timedelta(minutes=10),
    )
