from fastapi import APIRouter
from services.partners import check_user, count_users

router = APIRouter()


@router.get("/check-user", response_model=dict)
async def check_user_route(user_id: int, source: str) -> dict:
    return check_user(user_id, source)


@router.get("/count-users", response_model=dict)
async def count_users_route(source: str) -> dict:
    return count_users(source)
