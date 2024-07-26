from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client
from config import TASK_BOUNTIES

mongo_db_client: MongoClient = get_mongo_db_client()

mongo_db_client['task_bounties'].drop()

mongo_db_client['task_bounties'].insert_many(TASK_BOUNTIES)
