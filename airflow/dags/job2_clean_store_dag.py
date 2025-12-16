from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow")
from src.job2_cleaner import run_cleaner

with DAG(
    dag_id="dag2_clean_and_store",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["weather", "batch", "sqlite"]
) as dag:

    clean_and_store = PythonOperator(
        task_id="clean_kafka_and_store_sqlite",
        python_callable=run_cleaner
    )
