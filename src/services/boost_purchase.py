from pymongo import MongoClient
from bson import ObjectId
from utils.pymongo_get_database import get_mongo_db_client

mongo_db_client: MongoClient = get_mongo_db_client()


def create_boost_purchase(boost_purchase: dict) -> dict:
    result = mongo_db_client['boost_purchases'].insert_one(boost_purchase)

    boost_purchase['_id'] = ObjectId(result.inserted_id)

    return boost_purchase


def get_boost_purchases(sort=None, skip=0, limit=0) -> object:
    if sort is None:
        sort = {"created_at": -1}

    return mongo_db_client['boost_purchases'].aggregate([
        {
            "$match": {}
        },
        {
            "$sort": sort
        },
        {
            "$facet": {
                "data": [
                    {"$skip": skip},
                    {"$limit": limit}
                ],
                "pagination": [
                    {"$count": "total"}
                ]
            }
        }
    ])


def get_boost_purchase(_id) -> dict:
    return mongo_db_client['boost_purchases'].find_one({"_id": ObjectId(_id)})


def check_if_boost_purchase_exist(user_tg_id, boost, level) -> bool:
    boost_purchase = mongo_db_client['boost_purchases'].find_one(
        {
            "user_tg_id": user_tg_id,
            "boost": boost,
            "level": level
        }
    )

    return bool(boost_purchase)
