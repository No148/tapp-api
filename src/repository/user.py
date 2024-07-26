from repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    collection = 'users'

    @classmethod
    def get_leaderboard(cls, sort=None, skip: int = 0, limit: int = 250):
        if not sort:
            sort = {'taps': -1}

        return cls.mongo_db_client[cls.collection].aggregate([
            {
                "$match": {}
            },
            {
                "$facet": {
                    "data": [

                        {
                            "$lookup": {
                                "from": "referrals",
                                "localField": "id",
                                "foreignField": "referrer_id",
                                "as": "referrals"
                            }
                        },
                        {
                            "$project": {
                                "_id": {"$toString": "$_id"},
                                "id": 1,
                                "taps": 1,
                                "raw_taps": 1,
                                "points": 1,
                                "level_info": 1,
                                "first_name": 1,
                                "last_name": 1,
                                "username": 1,
                                "created_at": 1,
                                "updated_at": 1,
                                "referrals_count": {"$size": "$referrals"}
                            }
                        },
                        {"$sort": sort},
                        {"$skip": skip},
                        {"$limit": limit},
                    ],
                    "pagination": [
                        {"$count": "total"}
                    ]
                }
            }
        ])
