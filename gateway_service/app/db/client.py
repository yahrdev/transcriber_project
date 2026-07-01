"""
Provides CRUD operations for job documents in MongoDB.
"""

from pymongo import MongoClient

# TODO: replace root Mongo credentials with service-specific user for production setup


def generate_db(settings):

    print("current settings - ", settings.settings_name)
    client = MongoClient(settings.mongo_url)
    db = client.get_database(settings.db_name)
    return db.get_collection(settings.collection_name)





