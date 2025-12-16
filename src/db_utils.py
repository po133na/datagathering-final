import sqlite3
from pathlib import Path

DB_PATH = Path("/opt/airflow/data/app.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        humidity INTEGER,
        pressure INTEGER,
        wind_speed REAL,
        weather_main TEXT,
        weather_desc TEXT,
        event_time TEXT,
        ingestion_time TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        date TEXT,
        city TEXT,
        avg_temp REAL,
        min_temp REAL,
        max_temp REAL,
        avg_humidity REAL,
        record_count INTEGER,
        PRIMARY KEY (date, city)
    )
    """)

    conn.commit()
    conn.close()