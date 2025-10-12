import json
from pathlib import Path
from typing import List

from pymongo import MongoClient, ReplaceOne


def _read_payload(source: Path) -> List[dict]:
    return json.loads(source.read_text(encoding="utf-8"))


def load_data_to_mongo(
    topic: str, input_json_path: str, mongo_uri: str, database: str = "youtube"
):
    source_path = Path(input_json_path)
    documents = _read_payload(source_path)

    with MongoClient(mongo_uri) as client:
        collection = client[database][topic]
        collection.create_index("videoId", unique=True)

        operations = [
            ReplaceOne({"videoId": item["videoId"]}, item, upsert=True)
            for item in documents
        ]
        if operations:
            collection.bulk_write(operations, ordered=False)

    try:
        source_path.unlink()
    except FileNotFoundError:
        pass
