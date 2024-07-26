from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client

mongo_db_client: MongoClient = get_mongo_db_client()

users = mongo_db_client['users'].find()
counter = 0

for user in users:
    if "auto_farming_boost" not in user["boosters"]:
        user["boosters"]["auto_farming_boost"] = {
            "start_farming_date": None,
            "finish_farming_date": None,
            "max_farm_points": 0
        }

        mongo_db_client['users'].update_one({"_id": user['_id']}, {"$set": {"boosters": user['boosters']}})
        counter += 1

        print(f"Added auto_farming_boost to user {user['_id']} ({counter})")
