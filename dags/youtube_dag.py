import json
from datetime import datetime
from pathlib import Path

from airflow.operators.python import PythonOperator
from fetch_youtube_data import fetch_videos_to_json
from load_data_to_mongo import load_data_to_mongo

from airflow import DAG

DAG_ID = "is459_assignment_youtube"
BASE_DIR = Path(__file__).resolve().parent
TOPIC_FILE = BASE_DIR / "topic.txt"


def read_topic():
    return TOPIC_FILE.read_text(encoding="utf-8").strip()


def make_paths():
    topic = read_topic()
    out_json = BASE_DIR / f"{topic}.json"
    return {"topic": topic, "json_path": str(out_json)}


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2025, 10, 1),
    schedule=None,
    catchup=False,
    description="Fetch 100 YouTube videos for a topic then load to MongoDB",
    tags=["assignment", "youtube", "mongo"],
) as dag:

    def task_fetch(**_):
        info = make_paths()
        # fetch and save JSON
        fetch_videos_to_json(
            topic=info["topic"], output_json_path=info["json_path"], max_results=100
        )
        # return for logging
        return json.dumps(info)

    def task_load(**_):
        info = make_paths()
        load_data_to_mongo(
            topic=info["topic"],
            input_json_path=info["json_path"],
            mongo_uri="mongodb://host.docker.internal:27017",
            database="youtube",
        )
        return f"Loaded {info['json_path']} into MongoDB collection '{info['topic']}' and removed file."

    fetch_task = PythonOperator(
        task_id="fetch_youtube_data",
        python_callable=task_fetch,
    )

    load_task = PythonOperator(
        task_id="load_data_to_mongo",
        python_callable=task_load,
    )

    fetch_task >> load_task
