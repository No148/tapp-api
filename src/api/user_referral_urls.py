from fastapi import APIRouter, HTTPException, Depends
from models import UserReferralUrl
from services.user_referral_url import (
    create_user_referral_url,
    get_user_referral_urls,
    get_random_referral_urls,
    increase_referrer_count
)
from services.pagination import PaginatedParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=UserReferralUrl | dict)
async def create_user_referral_url_api(user_referral_url: UserReferralUrl, is_parse_metadata: bool = True, is_validate_only: bool = False) -> UserReferralUrl | dict:
    return await create_user_referral_url(user_referral_url, is_parse_metadata, is_validate_only)


@router.get("/", response_model=PaginatedResponse[UserReferralUrl])
async def get_many(q: PaginatedParams = Depends(), user_tg_id: int = None, is_valid: bool = None) -> dict:
    return await get_user_referral_urls(q.offset, q.sort, q.limit, user_tg_id, is_valid)


@router.get("/random", response_model=list[UserReferralUrl])
async def get_random(exclude_ids: str = '', exclude_project_urls: str = '', random_count: int = 5) -> list[dict]:
    return get_random_referral_urls(exclude_ids, exclude_project_urls, random_count)


@router.post("/{_id}/increase-referrer-count", response_model=UserReferralUrl)
async def do_increase_referrer_count(_id: str) -> UserReferralUrl:
    result = increase_referrer_count(_id)

    if 'error_msg' in result:
        raise HTTPException(status_code=result['error_code'], detail=result['error_msg'])

    return result
