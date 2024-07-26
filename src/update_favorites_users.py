from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client

mongo_db_client: MongoClient = get_mongo_db_client()

users = mongo_db_client['users'].find()
counter = 0

for user in users:
    prepared_favorite_projects = {}

    if 'favorite_projects' in user:
        for f_project_id in user['favorite_projects']:
            prepared_favorite_projects[f_project_id] = {"last_opened_date": None}

    mongo_db_client['users'].update_one({"_id": user['_id']}, {"$set": {"favorite_projects": prepared_favorite_projects}})
    counter += 1

    print(f"Updated favorite_projects to user {user['_id']} ({counter})")
