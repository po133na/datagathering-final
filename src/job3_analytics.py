import pandas as pd
from datetime import date, timedelta
from src.db_utils import get_connection, init_db


def run_daily_analytics():
    """
    Daily analytics job:
    - reads cleaned events from SQLite
    - computes daily aggregates per city
    - writes results into daily_summary table
    """

    init_db()
    conn = get_connection()

    
    target_date = (date.today() - timedelta(days=1)).isoformat()

    query = """
        SELECT
            city,
            temperature,
            humidity,
            pressure,
            wind_speed,
            event_time
        FROM events
        WHERE date(event_time) = ?
    """

    df = pd.read_sql_query(query, conn, params=(target_date,))

    if df.empty:
        print(f"No data available for date {target_date}")
        conn.close()
        return

    df["date"] = target_date

    summary = (
        df.groupby(["date", "city"])
        .agg(
            avg_temperature=("temperature", "mean"),
            min_temperature=("temperature", "min"),
            max_temperature=("temperature", "max"),
            avg_humidity=("humidity", "mean"),
            avg_pressure=("pressure", "mean"),
            avg_wind_speed=("wind_speed", "mean"),
            records_count=("temperature", "count")
        )
        .reset_index()
    )

    
    conn.execute(
        "DELETE FROM daily_summary WHERE date = ?",
        (target_date,)
    )

    summary.to_sql(
        "daily_summary",
        conn,
        if_exists='replace',
        index=False
    )

    conn.commit()
    conn.close()

    print(f"Daily summary successfully written for {target_date}")
