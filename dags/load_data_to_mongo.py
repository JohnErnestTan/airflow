import json
from pathlib import Path
from typing import List

from pymongo import MongoClient, ReplaceOne


def _read_payload(source: Path) -> List[dict]:
    # Reads and parses the JSON file into a list of dictionaries.
    return json.loads(source.read_text(encoding="utf-8"))


def load_data_to_mongo(
    # YouTube video data from the response file into a MongoDB collection.
    topic: str, input_json_path: str, mongo_uri: str, database: str = "youtube"
):  
     # Convert string path to Path object for easier file handling
    source_path = Path(input_json_path)
    payload = _read_payload(source_path)

    with MongoClient(mongo_uri) as client:
        collection = client[database][topic]
        collection.create_index("videoId", unique=True)

        replacements = [
            ReplaceOne({"videoId": item["videoId"]}, item, upsert=True)
            for item in payload
        ]
        if replacements:
            collection.bulk_write(replacements, ordered=False)

    try:
        source_path.unlink()
    except FileNotFoundError:
        pass
