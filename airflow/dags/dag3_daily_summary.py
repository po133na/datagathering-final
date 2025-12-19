from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow")

from src.job3_analytics import run_daily_analytics


with DAG(
    dag_id="dag3_daily_summary",
    max_active_runs=1,
    concurrency=1,
    start_date=datetime(2025, 12, 15),
    schedule_interval="@daily",
    catchup=False,
    tags=["weather", "analytics", "sqlite"]
) as dag:

    daily_summary_task = PythonOperator(
        task_id="compute_daily_weather_summary",
        python_callable=run_daily_analytics
    )
