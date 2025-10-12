import json
import os
from pathlib import Path

from pymongo import MongoClient, ReplaceOne


def load_data_to_mongo(topic: str, input_json_path: str, mongo_uri: str, database: str = "youtube"):
    client = MongoClient(mongo_uri)
    db = client[database]
    coll = db[topic]
    coll.create_index("videoId", unique=True)

    p = Path(input_json_path)
    items = json.loads(p.read_text(encoding="utf-8"))

    ops = [ReplaceOne({"videoId": d["videoId"]}, d, upsert=True) for d in items]
    if ops:
        coll.bulk_write(ops, ordered=False)
    try:
        p.unlink()
    except FileNotFoundError:
        pass

    client.close()
