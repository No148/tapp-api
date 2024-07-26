from fastapi import APIRouter
from services.statistics import get_statistics

router = APIRouter()


@router.get("/", response_model=any({}))
async def get_many() -> dict:
    return await get_statistics()

