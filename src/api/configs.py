from fastapi import APIRouter
from models import USER_LEVELS
from config import BOOSTERS

router = APIRouter()


@router.get("/", response_model=dict)
async def get_configs() -> dict:
    boosters_config = BOOSTERS
    user_levels = USER_LEVELS

    return {
        'boosters_config': boosters_config,
        'tap_levels': user_levels
    }
