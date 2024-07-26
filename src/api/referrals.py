from fastapi import APIRouter, HTTPException, Depends
from models import Referral
from services.referral import create_referral, get_referrals, get_multilevel_referrals_for_user
from services.pagination import PaginatedParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=Referral)
async def create(referral: Referral) -> Referral:
    result = await create_referral(referral)

    if 'error_msg' in result:
        raise HTTPException(status_code=result['error_code'], detail=result['error_msg'])

    return result


@router.get("/", response_model=PaginatedResponse[Referral])
async def get_many(q: PaginatedParams = Depends(), referrer: int | None = None) -> dict:
    return get_referrals(q.offset, q.sort, q.limit, referrer)


@router.get("/multilevel", response_model=dict)
async def get_multilevel_referrals_for_user_api(user_tg_id: int = None, deep_level: int = 1) -> dict:
    return get_multilevel_referrals_for_user(user_tg_id, deep_level)
