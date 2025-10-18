import json
from datetime import datetime
from pathlib import Path

from airflow.operators.python import PythonOperator
from fetch_youtube_data import fetch_videos_to_json
from load_data_to_mongo import load_data_to_mongo

from airflow import DAG

_DAG_ID = "is459_assignment_youtube"
_ROOT = Path(__file__).resolve().parent
_TOPIC_PATH = _ROOT / "topic.txt"
_MONGO_URI = "mongodb://host.docker.internal:27017"
_MONGO_DB = "anime_youtube"
_VIDEO_TARGET = 100


def _read_topic() -> str:
    topic_value = _TOPIC_PATH.read_text(encoding="utf-8").strip()
    if not topic_value:
        raise ValueError("Topic file cannot be empty.")
    return topic_value


def _artifact_paths():
    topic_name = _read_topic()
    payload_path = _ROOT / f"{topic_name}.json"
    return topic_name, payload_path


with DAG(
    dag_id=_DAG_ID,
    start_date=datetime(2025, 10, 1),
    schedule=None,
    catchup=False,
) as dag:

    def _run_fetch(**_):
        topic_name, payload_path = _artifact_paths()
        fetch_videos_to_json(
            topic=topic_name,
            output_json_path=str(payload_path),
            max_results=_VIDEO_TARGET,
        )
        return json.dumps({"topic": topic_name, "json_path": str(payload_path)})

    def _run_load(**_):
        topic_name, payload_path = _artifact_paths()
        load_data_to_mongo(
            topic=topic_name,
            input_json_path=str(payload_path),
            mongo_uri=_MONGO_URI,
            database=_MONGO_DB,
        )
        return f"{payload_path} stored in MongoDB collection '{topic_name}' and removed locally."

    fetch_task = PythonOperator(
        task_id="fetch_youtube_data",
        python_callable=_run_fetch,
    )

    load_task = PythonOperator(
        task_id="load_data_to_mongo",
        python_callable=_run_load,
    )

    fetch_task >> load_task
