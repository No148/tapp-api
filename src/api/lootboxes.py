from fastapi import APIRouter, Depends
from models import LootBox, LootBoxActivateBody
from repository import LootboxRepository
from services.lootbox import activate_lootbox, get_lootbox_or_fail, get_lootbox_detail, get_lootboxes_by_user
from services.pagination import PaginatedParams, PaginatedResponse

router = APIRouter()
lootbox_repository = LootboxRepository()


@router.get("/by-user/{user_id}", response_model=PaginatedResponse[LootBox])
async def get_lootboxes_by_user_route(user_id: int, q: PaginatedParams = Depends()) -> dict:
    return get_lootboxes_by_user(user_id, q.offset, q.sort, q.limit)


@router.get("/{lootbox_id}", response_model=LootBox)
async def get_lootbox_route(lootbox_id: str) -> LootBox:
    return get_lootbox_or_fail(lootbox_id)


@router.get("/{lootbox_id}/detail", response_model=dict)
async def get_lootbox_detail_route(lootbox_id: str) -> dict:
    return get_lootbox_detail(lootbox_id)


@router.post("/{lootbox_id}/activate_lootbox", response_model=LootBox)
async def activate_lootbox_route(lootbox_id: str, data: LootBoxActivateBody) -> LootBox:
    return await activate_lootbox(lootbox_id, data.user)
