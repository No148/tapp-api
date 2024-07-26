from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client


class BaseRepository:
    mongo_db_client: MongoClient = get_mongo_db_client()
    collection = None

    @classmethod
    def get_one(cls, query=None) -> dict:
        if not query:
            query = {}

        return cls.mongo_db_client[cls.collection].find_one(query)

    @classmethod
    def get_many(cls, query=None) -> list[dict]:
        if not query:
            query = {}

        return cls.mongo_db_client[cls.collection].find(query)

    @classmethod
    def create_one(cls, obj: dict) -> dict:
        result = cls.mongo_db_client[cls.collection].insert_one(obj)

        if result and result.inserted_id:
            obj['_id'] = ObjectId(result.inserted_id)

        return obj

    @classmethod
    def update_one(cls, query: dict, update: dict) -> dict:
        if '$set' not in update:
            update['$set'] = {}

        update['$set']['updated_at'] = datetime.utcnow()

        return cls.mongo_db_client[cls.collection].update_one(
            query,
            update
        )

    @classmethod
    def update_many(cls, query: dict, obj: dict) -> dict:
        obj['updated_at'] = datetime.utcnow()

        return cls.mongo_db_client[cls.collection].update_many(
            query,
            {"$set": obj}
        )

        # print(result.modified_count)
        #
        # if result and result.modified_count > 0:
        #     obj['updated_at'] = datetime.utcnow()
        #
        # return obj

    @classmethod
    def count_documents(cls, query=None) -> int:
        if not query:
            query = {}

        return cls.mongo_db_client[cls.collection].count_documents(query)

    @classmethod
    def aggregate(cls, query):
        return cls.mongo_db_client[cls.collection].aggregate(query)
