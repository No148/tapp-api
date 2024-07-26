from fastapi import APIRouter
from models import UserUpdate, Boost
from services.boost import boost_purchase

router = APIRouter()


@router.post("/purchase", response_model=UserUpdate)
async def purchase(boost: Boost) -> UserUpdate:
    return await boost_purchase(boost)
