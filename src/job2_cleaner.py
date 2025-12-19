import json
from kafka import KafkaConsumer
from datetime import datetime, timezone
from src.db_utils import get_connection, init_db

KAFKA_TOPIC = "raw_weather"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
GROUP_ID = "weather_batch_cleaner"

MAX_MESSAGES = 500
MAX_POLLS = 20
POLL_TIMEOUT_MS = 5000

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
            msg["fetched_at"],
        )
    except Exception:
        return None


def run_cleaner(**context):
    data_interval_start = context["data_interval_start"]
    data_interval_end = context["data_interval_end"]

    window_start = data_interval_start.astimezone(timezone.utc)
    window_end = data_interval_end.astimezone(timezone.utc)

    init_db()
    conn = get_connection()
    cur = conn.cursor()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    processed = 0

    try:
        for _ in range(MAX_POLLS):
            records = consumer.poll(timeout_ms=POLL_TIMEOUT_MS)
            if not records:
                break

            for _, messages in records.items():
                for message in messages:
                    msg = message.value

                    fetched_at = datetime.fromisoformat(
                        msg["fetched_at"]
                    ).astimezone(timezone.utc)

                    if not (window_start <= fetched_at < window_end):
                        continue

                    cleaned = clean_message(msg)
                    if not cleaned:
                        continue

                    cur.execute(
                        """
                        INSERT INTO events (
                            city, temperature, humidity, pressure,
                            wind_speed, weather_main, weather_desc,
                            event_time, ingestion_time
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        cleaned,
                    )

                    processed += 1
                    if processed >= MAX_MESSAGES:
                        break

                if processed >= MAX_MESSAGES:
                    break

            if processed >= MAX_MESSAGES:
                break

        conn.commit()

    finally:
        consumer.close()
        conn.close()

    print(
        f"Cleaner processed {processed} messages "
        f"from {window_start} to {window_end}"
    )
