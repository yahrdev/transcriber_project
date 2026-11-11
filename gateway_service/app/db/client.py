"""
Provides CRUD operations for job documents in MongoDB.
"""

from pymongo import MongoClient
from functools import lru_cache

# TODO: replace root Mongo credentials with service-specific user for production setup

@lru_cache
def get_mongo_client(mongo_url: str) -> MongoClient:
    return MongoClient(mongo_url)

def generate_db(settings):

    print("current settings - ", settings.settings_name)
    client = get_mongo_client(settings.mongo_url)
    db = client.get_database(settings.db_name)
    return db.get_collection(settings.collection_name)





