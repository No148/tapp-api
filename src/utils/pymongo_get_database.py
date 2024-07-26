from pymongo import MongoClient
from utils.env import MONGO_DB_NAME, MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD


def get_mongo_db_client():
    if not MONGO_HOST or not MONGO_PORT or not MONGO_DB_NAME:
        return None

    # Create a MongoClient instance
    client = MongoClient(MONGO_HOST, int(MONGO_PORT), username=MONGO_USERNAME, password=MONGO_PASSWORD, connectTimeoutMS=1440000, serverSelectionTimeoutMS=1440000)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[MONGO_DB_NAME]
