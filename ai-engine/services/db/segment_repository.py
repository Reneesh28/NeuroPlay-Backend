import os
from dotenv import load_dotenv
from services.db.mongo_client import get_db

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "segments")
BATCH_SIZE = 300


def get_collection():
    db = get_db()
    return db[COLLECTION_NAME]


def insert_segments_batch(segments):
    if not segments:
        return

    collection = get_collection()
    collection.insert_many(segments)