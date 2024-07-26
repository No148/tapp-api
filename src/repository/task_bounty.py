from repository.base_repository import BaseRepository


class TaskBountyRepository(BaseRepository):
    collection = 'task_bounties'

    @classmethod
    def get_task_bounties(cls, query = None, skip: int = 0, sort: str = None, limit: int = 100):
        if not query:
            query = {}

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
