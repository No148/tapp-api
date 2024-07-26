from fastapi import APIRouter, Depends
from api import configs
from api import users
from api import task_bounties
from api import referrals
from api import statistics
from api import boosters
from api import user_referral_urls
from api import projects
from api import lootboxes
from api import partners
from api import favorites
from api import auto_farming
from api import demo
from services.auth import api_key_auth
from services.auth import partners_api_key_auth

api_router = APIRouter()

api_router.include_router(
    configs.router,
    prefix="/configs",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    users.router,
    prefix="/users",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    task_bounties.router,
    prefix="/task-bounties",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    referrals.router,
    prefix="/referrals",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    statistics.router,
    prefix="/statistics",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    boosters.router,
    prefix="/boosters",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    user_referral_urls.router,
    prefix="/user-referral-urls",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    dependencies=[Depends(api_key_auth)]
)


api_router.include_router(
    lootboxes.router,
    prefix="/lootboxes",
    dependencies=[Depends(api_key_auth)]
)


api_router.include_router(
    partners.router,
    prefix="/partners",
    dependencies=[Depends(partners_api_key_auth)]
)

api_router.include_router(
    favorites.router,
    prefix="/favorites",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    auto_farming.router,
    prefix="/auto-farming",
    dependencies=[Depends(api_key_auth)]
)

api_router.include_router(
    demo.router,
    prefix="/demo",
    dependencies=[Depends(api_key_auth)]
)
