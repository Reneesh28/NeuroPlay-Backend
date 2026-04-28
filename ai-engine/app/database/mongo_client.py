import os
from pymongo import MongoClient

client = MongoClient(
    os.getenv("MONGO_URI"),
    maxPoolSize=20
)

db = client[os.getenv("DB_NAME", "neuroplay_dev")]