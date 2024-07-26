from repository.base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    collection = 'projects'

    @classmethod
    def check_if_project_exist(cls, url: str) -> bool:
        user_referral_url = cls.mongo_db_client[cls.collection].find_one(
            {
                "url": url
            }
        )

        return bool(user_referral_url)

    @classmethod
    def get_projects(cls, query: dict = None, limit=50, skip=0, sort=None):
        if not query:
            query = {}

        if not sort:
            sort = {'created_at': -1}

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
                    ],
                    "pagination": [
                        {"$count": "total"}
                    ]
                }
            }
        ])
