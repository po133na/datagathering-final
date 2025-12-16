import json
from kafka import KafkaConsumer
from datetime import datetime
from src.db_utils import get_connection, init_db

KAFKA_TOPIC = "raw_weather"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
GROUP_ID = "weather_batch_cleaner"

def clean_message(msg):
    try:
        main = msg["main"]
        wind = msg.get("wind", {})
        weather = msg.get("weather", [{}])[0]

        return (
            msg.get("name"),
            float(main["temp"]),
            int(main["humidity"]),
            int(main["pressure"]),
            float(wind.get("speed", 0.0)),
            weather.get("main"),
            weather.get("description"),
            datetime.utcfromtimestamp(msg["dt"]).isoformat(),
            msg["fetched_at"]
        )
    except Exception:
        return None

def run_cleaner():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    count = 0
    for message in consumer:
        cleaned = clean_message(message.value)
        if not cleaned:
            continue

        cur.execute("""
            INSERT INTO events (
                city, temperature, humidity, pressure,
                wind_speed, weather_main, weather_desc,
                event_time, ingestion_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cleaned)

        count += 1
        if count >= 500:
            break

    conn.commit()
    conn.close()
