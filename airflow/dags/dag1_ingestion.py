from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
from kafka import KafkaProducer


API_KEY = "f627c5a17d6b7374370f18d2b1db8a05"
CITIES = ["Almaty", "Astana", "Shymkent", "Aktobe", "Karaganda", "Oskemen"]
KAFKA_TOPIC = "raw_weather"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092" 


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


def fetch_and_send_weather():    
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    for city in CITIES:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            weather_data['fetched_at'] = datetime.now().isoformat()
            producer.send(KAFKA_TOPIC, value=weather_data)
            print(f"{city}: {weather_data['main']['temp']}°C")
            
        except Exception as e:
            print(f"Error fetching weather for {city}: {e}")
    
    producer.flush()
    producer.close()


with DAG(
    'dag1_weather_ingestion',
    default_args=default_args,
    description='weather data from API to Kafka',
    schedule_interval='*/1 * * * *', 
    catchup=False,
    tags=['weather', 'ingestion'],
) as dag:

    fetch_weather_task = PythonOperator(
        task_id='fetch_and_send_weather',
        python_callable=fetch_and_send_weather,
    )