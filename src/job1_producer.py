import requests
import json
from kafka import KafkaProducer
from datetime import datetime
import time
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITIES = ["Almaty", "Astana", "Shymkent", "Aktobe", "Karaganda", "Oskemen"]
KAFKA_TOPIC = "raw_weather"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    return response.json()


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


def send_to_kafka(producer, data):
    producer.send(KAFKA_TOPIC, value=data)
    producer.flush()


def run_producer(duration_minutes=60):
    producer = create_producer()
    print(f"Started weather producer at {datetime.now()}")
    print(f"Kafka topic: {KAFKA_TOPIC}")
    print(f"Cities: {CITIES}")
    print("-" * 50)
    
    end_time = time.time() + (duration_minutes * 60)
    
    while time.time() < end_time:
        for city in CITIES:
            try:
                weather_data = get_weather(city)
                
                weather_data['fetched_at'] = datetime.now().isoformat()
                
                send_to_kafka(producer, weather_data)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] sent: {city} - {weather_data['main']['temp']}°C")
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] error for {city}: {e}")
        
        print("-" * 50)
        time.sleep(60)  
    
    producer.close()
    print("Producer closed")


if __name__ == "__main__":
    run_producer(duration_minutes=60)