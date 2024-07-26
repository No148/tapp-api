from pymongo import MongoClient
from utils.pymongo_get_database import get_mongo_db_client

mongo_db_client: MongoClient = get_mongo_db_client()

users_collection = mongo_db_client['users']
boost_purchases_collection = mongo_db_client['boost_purchases']

# Iterate through all users
for user in users_collection.find():    
    # Sum up the prices of all purchases made by this user
    spent_points = boost_purchases_collection.aggregate([
        {'$match': {'user_id': user['_id']}},
        {'$group': {'_id': None, 'total_spent': {'$sum': '$price'}}}
    ])
    
    # Extract the total spent points
    total_spent = 0
    for result in spent_points:
        total_spent = result['total_spent']
    
    # Update the user's spent_points field
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'spent_points': total_spent}}
    )

print("Spent points updated for all users.")
