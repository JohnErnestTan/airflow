# BDA Airflow Assignment

## Prerequisites

-   Docker Desktop with Docker Compose
-   YouTube Data API v3 key stored as `YOUTUBE_API_KEY` in `.env`
-   Local MongoDB instance (or update the URI to your Atlas cluster)
-   Optional GUI: [MongoDB Compass](https://downloads.mongodb.com/compass/mongodb-compass-1.47.1-win32-x64.exe)

## Quick Start

```bash
# bring up the Airflow stack
docker-compose up -d

# bootstrap an admin user (run once)
docker-compose run airflow-worker airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
```

Access the Airflow UI at <http://localhost:8080> using the admin credentials above.

## Running the Assignment DAG

1. Set your topic in `dags/topic.txt` (e.g., `whatever topic you want`).
2. Ensure MongoDB is reachable at `mongodb://localhost:27017` or adjust the URI in `dags/youtube_dag.py`.
3. Trigger the DAG `is459_assignment_youtube` from the UI.
4. Monitor task logs:
    - `fetch_youtube_data` writes `<topic>.json` into the `dags/` folder.
    - `load_data_to_mongo` ingests the JSON into MongoDB and then deletes the file.
5. Verify documents in MongoDB via Compass or the Mongo shell (`mongo --host localhost --port 27017`).

## Tear Down

```bash
docker-compose down --volumes --remove-orphans
```

This stops and removes containers, volumes, and orphaned services. Re-run the quick start steps whenever you need a fresh environment.
