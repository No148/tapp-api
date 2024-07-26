from fastapi import APIRouter, Request, Depends
from models import User, UserUpdate, TaskBountyWithStatus
from services.referral import get_referrals_by_user_id, get_referrals_accumulated_rewards
from services.task_bounty import get_user_task_bounties_by_id
from services.user import create_user, get_or_upsert_user, add_points, add_taps, add_task_bounty, claim_task_bounty, update_user, get_user_by_id, get_user_boosters_by_id, bot_send_invite_friends, activate_interval_booster, claim_daily_reward_task, get_leaderboard, referrals_claim_accumulated_reward
from services.pagination import PaginatedParams, PaginatedResponse

router = APIRouter()


# POST
@router.post("/", response_model=User)
async def create(user: User) -> User:
    return await create_user(user)


@router.get("/leaderboard", response_model=list[dict])
async def get_leaderboard_api(user_id: int = None, sort: str = '-taps', limit: int = 250) -> dict:
    return get_leaderboard(user_id, sort, limit)


@router.post("/get-or-upsert", response_model=User)
async def get_or_upsert(user: User, request: Request) -> User:
    print(await request.json())
    return await get_or_upsert_user(user)


@router.post("/{user_id}/add-points", response_model=User)
async def add_points_by_user_id(user_id: int, user_update: UserUpdate) -> User:
    return await add_points(user_id, user_update)


@router.post("/{user_id}/add-taps", response_model=User)
async def add_taps_by_user_id(user_id: int, user_update: UserUpdate, request: Request) -> UserUpdate:
    return await add_taps(user_id, user_update)


@router.post("/{user_id}/add-task-bounty/{task_bounty_id}", response_model=UserUpdate)
async def do_task(user_id: int, task_bounty_id: str, body: dict = {}) -> UserUpdate:
    return await add_task_bounty(user_id, task_bounty_id, body)


@router.post("/{user_id}/claim-task-bounty/{task_bounty_id}", response_model=UserUpdate)
async def claim_task(user_id: int, task_bounty_id: str) -> UserUpdate:
    return await claim_task_bounty(user_id, task_bounty_id)


@router.post("/{user_id}/claim-daily-reward-task", response_model=UserUpdate)
async def claim_daily_reward_task_route(user_id: int) -> UserUpdate:
    return await claim_daily_reward_task(user_id)


@router.get("/{user_id}/task-bounties", response_model=PaginatedResponse[TaskBountyWithStatus])
async def get_user_task_bounties(user_id: int, q: PaginatedParams = Depends()) -> dict:
    return await get_user_task_bounties_by_id(user_id, q.offset, q.sort, q.limit)


# PATCH/PUT
@router.patch("/{user_id}", response_model=User)
async def update_by_id(user_id: int, user: UserUpdate) -> UserUpdate:
    return update_user(user_id, user)


# GET
@router.get("/{user_id}", response_model=User)
async def get_by_id(user_id: int) -> dict:
    return await get_user_by_id(user_id)


@router.get("/{user_id}/referrals", response_model=dict)
async def get_referrals_by_id(user_id: int, q: PaginatedParams = Depends()) -> dict:
    return get_referrals_by_user_id(user_id, q.offset, q.sort, q.limit)


@router.get("/{user_id}/referrals/accumulated-rewards", response_model=dict)
async def get_referrals_accumulated_rewards_route(user_id: int) -> dict:
    return get_referrals_accumulated_rewards(user_id)


@router.get("/{user_id}/boosters", response_model=dict)
async def get_user_boosters(user_id: int) -> dict:
    return await get_user_boosters_by_id(user_id)


@router.post("/{user_id}/boosters/{interval_booster_key}/activate", response_model=bool)
async def activate_interval_booster_route(user_id: int, interval_booster_key: str) -> bool:
    return await activate_interval_booster(user_id, interval_booster_key)


@router.post("/{user_id}/bot-send-invite-friends")
async def bot_send_invite_friends_route(user_id: int) -> bool:
    return await bot_send_invite_friends(user_id)


@router.post("/{user_id}/referrals/claim-accumulated-reward")
async def referrals_claim_accumulated_reward_route(user_id: int) -> bool:
    return referrals_claim_accumulated_reward(user_id)
