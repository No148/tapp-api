from datetime import datetime
from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client

mongo_db_client: MongoClient = get_mongo_db_client()


async def get_statistics() -> any({}):
    total_data = list(mongo_db_client['users'].aggregate([{
        "$group": {
            "_id": None,
            "total_points": {"$sum": "$points"},
            "total_taps": {"$sum": "$raw_taps"},
            "total_players": {"$sum": 1}
        }
    }]))

    new_users_today = list(mongo_db_client['users'].aggregate([
        {
            "$addFields": {"creation_date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}},
        },
        {
            "$match": {
                "creation_date": {
                    "$eq": f"{datetime.utcnow().strftime('%Y-%m-%d')}"
                }
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "new_users_today": {"$sum": 1}
            }
        }
    ]))

    result = {
        "total_points": 0,
        "total_taps": 0,
        "total_players": 0,
        "new_players_today": 0,
        "count_dau_1_day": 0,
        "count_dau_3_day": 0
    }

    dau_users = list(mongo_db_client['users'].aggregate([
        {
            "$project": {
                "item": 1,
                "dau_1_day": { # Set to 1 if daily_reward_progress = 1
                    "$cond": [{"$eq": [{"$dateToString": {"format": "%Y-%m-%d", "date": "$last_login_date"}}, datetime.utcnow().strftime('%Y-%m-%d')]}, 1, 0]
                },
                "dau_3_day": { # Set to 1 if daily_reward_progress = 3
                    "$cond":[{"$and": [
                        {"$gte": ["$daily_reward_progress", 3]},
                        {"$eq": [{"$dateToString": {"format": "%Y-%m-%d", "date": "$last_login_date"}}, datetime.utcnow().strftime('%Y-%m-%d')]}
                    ]}, 1, 0]
                }
            }
        },
        {
            "$group": {
                "_id": "$item",
                "count_dau_1_day": {"$sum": "$dau_1_day"},
                "count_dau_3_day": {"$sum": "$dau_3_day"}
            }
        }
    ]))

    if dau_users and len(dau_users) > 0:
        result["count_dau_1_day"] = dau_users[0]["count_dau_1_day"]
        result["count_dau_3_day"] = dau_users[0]["count_dau_3_day"]

    if total_data:
        result["total_points"] = total_data[0]["total_points"]
        result["total_taps"] = total_data[0]["total_taps"]
        result["total_players"] = total_data[0]["total_players"]

    if new_users_today:
        result["new_players_today"] = new_users_today[0]["new_users_today"]

    return result
