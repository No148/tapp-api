from fastapi import APIRouter
from models import UserUpdate, User
from services.auto_farming import activate_farming, claim_farming_points, get_user_farming_data

router = APIRouter()


@router.post("/{user_id}/activate", response_model=User)
async def activate_farming_api(user_id: int) -> UserUpdate:
    return activate_farming(user_id)


@router.post("/{user_id}/claim", response_model=User)
async def claim_farming_points_api(user_id: int) -> UserUpdate:
    return claim_farming_points(user_id)


@router.get("/{user_id}", response_model=dict)
async def get_user_farming_data_api(user_id: int) -> dict:
    return get_user_farming_data(user_id)
