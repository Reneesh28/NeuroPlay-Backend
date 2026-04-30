import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

_client = None


def get_db():
    global _client

    if _client is None:
        _client = MongoClient(MONGO_URI)

    return _client[DB_NAME]