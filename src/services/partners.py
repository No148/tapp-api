from models import User
from repository import UserRepository
from services.user import get_user

user_repository = UserRepository()


def check_user(user_id: int, source: str) -> dict:
    user = get_user(user_id)

    if user:
        user = User(**user)

    return {
        'isMember': bool(user),
        'isRef': bool(user) and user.utm_source == source,
    }


def count_users(source: str) -> dict:
    count = user_repository.count_documents({
        'utm_source': source
    })

    return {
        'count': count
    }
