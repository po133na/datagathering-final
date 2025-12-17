# Real-Time Weather Data Pipeline with Airflow, Kafka, and SQLite

This project implements a complete **streaming + batch data pipeline** for
collecting, cleaning, storing, and analyzing real-time weather data.
The system is fully containerized using **Docker Compose** and orchestrated
with **Apache Airflow**.

---
## API
https://api.openweathermap.org

## Project Overview
The pipeline processes real-world, frequently updating weather data from the
**OpenWeather API** and consists of three Airflow DAGs:

1. **DAG 1 – Continuous Ingestion**
   - Fetches weather data every minute
   - Publishes raw JSON messages to Kafka

2. **DAG 2 – Hourly Cleaning & Storage**
   - Reads messages from Kafka
   - Cleans and normalizes data
   - Stores cleaned records in SQLite

3. **DAG 3 – Daily Analytics**
   - Aggregates daily weather statistics
   - Writes results into a summary table in SQLite

---

## System Architecture


OpenWeather API
↓
Airflow DAG 1 (Ingestion)
↓
Kafka Topic (raw_weather)
↓
Airflow DAG 2 (Cleaning)
↓
SQLite (events table)
↓
Airflow DAG 3 (Analytics)
↓
SQLite (daily_summary table)


---

## Docker Services

The system is deployed using `docker-compose.yml` with the following services:

| Service | Description |
|-------|------------|
| Zookeeper | Coordinates Kafka brokers |
| Kafka | Message broker for streaming data |
| PostgreSQL | Airflow metadata database |
| Airflow Webserver | Airflow UI and DAG execution |
| Airflow Scheduler | Triggers and schedules DAGs |

Kafka is internally accessible at `kafka:9092` and externally at `localhost:9092`.

---

## Repository Structure

```

project/
│ README.md
│ requirements.txt
├─ src/
│ ├─ job1_producer.py
│ ├─ job2_cleaner.py
│ ├─ job3_analytics.py
│ └─ db_utils.py
├─ airflow/
│ └─ dags/
│ ├─ dag1_weather_ingestion.py
│ ├─ dag2_clean_store_dag.py
│ └─ dag3_daily_summary.py
├─ data/
│ └─ app.db
├─ docker-compose.yml
└─ report/
└─ report.pdf

````

---

## API Information

- **API Provider:** OpenWeather
- **Data Type:** Real-time weather data
- **Format:** JSON
- **Update Frequency:** Every few minutes
- **Cities Monitored:**
  - Almaty
  - Astana
  - Shymkent
  - Aktobe
  - Karaganda
  - Oskemen

---

## Kafka Topic

**Topic Name:** `raw_weather`

Each message contains:
- City name
- Temperature (°C)
- Humidity
- Pressure
- Wind speed
- Weather description
- Event timestamp
- Ingestion timestamp

---

## Data Cleaning Rules (DAG 2)

- Type conversion for numeric fields
- Missing wind speed replaced with `0.0`
- Invalid or malformed messages skipped
- Timestamps normalized to ISO format

---

## SQLite Database Schema

### `events` Table (Cleaned Data)

| Column | Type |
|------|------|
| id | INTEGER (PK) |
| city | TEXT |
| temperature | REAL |
| humidity | INTEGER |
| pressure | INTEGER |
| wind_speed | REAL |
| weather_main | TEXT |
| weather_desc | TEXT |
| event_time | TEXT |
| ingestion_time | TEXT |

### `daily_summary` Table (Analytics)

| Column | Type |
|------|------|
| date | TEXT |
| city | TEXT |
| avg_temperature | REAL |
| min_temperature | REAL |
| max_temperature | REAL |
| avg_humidity | REAL |
| avg_pressure | REAL |
| avg_wind_speed | REAL |
| records_count | INTEGER |

---

## How to Run the Project

### Start all services
```bash
docker-compose up -d
````

### Access Airflow UI

* URL: [http://localhost:8080](http://localhost:8080)
* Username: `admin`
* Password: `admin`

### Enable DAGs

Enable the following DAGs in order:

1. `dag1_weather_ingestion`
2. `dag2_clean_and_store`
3. `dag3_daily_summary`

---

## Results

* Raw weather data is streamed into Kafka continuously
* Cleaned data is stored hourly in SQLite
* Daily aggregated statistics are computed per city
* Results are stored in the `daily_summary` table

---

## Technologies Used

* Python 3.10
* Apache Airflow 2.7
* Apache Kafka
* Docker & Docker Compose
* SQLite
* PostgreSQL (Airflow metadata)
* Pandas

---

## Team Members

| Full Name | ID         | GitHub                                     |
| --------- | ---------- | ------------------------------------------ |
| Stelmakh Polina | 22B030588 | [Stelmakh](https://github.com/po133na) |
| Suanbekova Aisha | 22B030589 | [Suanbekova](https://github.com/Sunbekova) |
| Nursovet Iman | [22B030416] | [Nursovet](https://github.com/b0ogiman) |

---

## Report

A detailed technical report describing the architecture, implementation,
and results is available in:

```
report/report.pdf
```

---
