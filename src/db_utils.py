import sqlite3
from pathlib import Path

DB_PATH = Path("/opt/airflow/data/app.db")


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        isolation_level=None
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Cleaned events table (from DAG 2)
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

    # Daily analytics summary table (from DAG 3)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_summary (
        date TEXT,
        city TEXT,
        avg_temperature REAL,
        min_temperature REAL,
        max_temperature REAL,
        avg_humidity REAL,
        avg_pressure REAL,
        avg_wind_speed REAL,
        records_count INTEGER,
        PRIMARY KEY (date, city)
    )
    """)

    conn.commit()
    conn.close()
