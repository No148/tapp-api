import re

from repository.base_repository import BaseRepository


class UserReferralUrlRepository(BaseRepository):
    collection = 'user_referral_urls'

    @classmethod
    def check_if_user_referral_url_exist(cls, user_tg_id: int, url: str) -> bool:
        url = re.escape(url)

        user_referral_url = cls.mongo_db_client[cls.collection].find_one(
            {
                "user_tg_id": {"$eq": user_tg_id},
                "url": {"$regex": url, "$options": "i"}
            }
        )

        return bool(user_referral_url)

    @classmethod
    def get_user_referral_urls(cls, query=None, limit=100, skip=0, sort=None):
        if not query:
            query = {}

        if not sort:
            sort = {"created_at": -1}

        return cls.mongo_db_client[cls.collection].aggregate([
            {
                "$match": query
            },
            {
                "$sort": sort
            },
            {
                "$facet": {
                    "data": [
                        {"$skip": skip},
                        {"$limit": limit},
                        {
                            "$lookup": {
                                "from": "projects",
                                "localField": "project_id",
                                "foreignField": "_id",
                                "as": "projects"
                            }
                        },
                        {
                            "$project": {
                                "_id": 1,
                                "url": 1,
                                "user_tg_id": 1,
                                "referrer_count": 1,
                                "is_valid": 1,
                                "project_id": 1,
                                "created_at": 1,
                                "updated_at": 1,
                                "project": {"$first": "$projects"}
                            }
                        },
                        {
                            "$project": {
                                "_id": {"$toString": "$_id"},
                                "url": 1,
                                "user_tg_id": 1,
                                "referrer_count": 1,
                                "is_valid": 1,
                                "project_id": {"$toString": "$project_id"},
                                "created_at": 1,
                                "updated_at": 1,
                                "project": {
                                    "_id": {"$toString": "$project._id"},
                                    "url": "$project.url",
                                    "title": "$project.title",
                                    "description": "$project.description",
                                    "image_url": "$project.image_url",
                                    "created_at": "$project.created_at",
                                    "updated_at": "$project.updated_at"
                                }
                            }
                        }
                    ],
                    "pagination": [
                        {"$count": "total"}
                    ]
                }
            }
        ])

    @classmethod
    def delete_one(cls, query=None):
        if not query:
            query = {}

        result = None

        if query:
            result = cls.mongo_db_client[cls.collection].delete_one(query)

        if result and 'deleted_count' in result:
            return result.deleted_count

        return 0
