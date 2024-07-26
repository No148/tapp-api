import random
import services.user as user_service
import services.referral as referral_service
import telegram

from bson import ObjectId
from config import bot_menu_buttons
from models import User, UserUpdate, LootBox, LootBoxUpdate, UserForLootbox, Referral
from repository import LootboxRepository, UserRepository
from services.pagination import paginate
from fastapi import HTTPException
from utils.env import BOT_TOKEN

lootbox_repository = LootboxRepository()
user_repository = UserRepository()


def update_lootbox_by_id(lootbox_id: str, model_update: LootBoxUpdate) -> dict:
    model_update_dict = model_update.model_dump(exclude_unset=True)

    lootbox_repository.update_one(
        query={"_id": ObjectId(lootbox_id)},
        update={"$set": model_update_dict}
    )

    return model_update_dict


def generate_and_create_lootbox(owner: int):
    model = LootBox(
        owner=owner,
        reward={
            'points': random.randint(1000, 10000),
            'usdt': random.randint(1, 10) / 100,
            'ton': random.randint(1, 10) / 1000
        },
        activated=False,
    )
    model_dict = model.model_dump(exclude=model.get_excluded_fields_for_update())

    lootbox_repository.create_one(model_dict)


def get_lootbox(lootbox_id: str) -> LootBox:
    return LootBox(**lootbox_repository.get_one(query={'_id': ObjectId(lootbox_id)}))


def get_lootbox_or_fail(lootbox_id: str) -> LootBox:
    lootbox = None

    try:
        lootbox = get_lootbox(lootbox_id)
    except Exception:
        pass

    if not lootbox:
        raise HTTPException(status_code=404, detail='Lootbox not found')

    return lootbox


def get_lootbox_detail(lootbox_id: str) -> dict:
    result = {
        'lootbox': get_lootbox_or_fail(lootbox_id)
    }

    user = UserForLootbox(**user_service.get_user_or_fail(result['lootbox'].owner))

    result['owner'] = {
        'id': user.id,
        'full_name': user.full_name,
        'username': user.username,
        'username_or_name': user.username_or_name
    }

    return result


def get_lootboxes_by_user(user_id: int, skip: int = 0, sort: str = None, limit: int = 50) -> dict:
    query = [
        {
            "$match": {"owner": user_id}
        },
        {
            "$sort": sort
        },
        {
            "$facet": {
                "data": [
                    {"$skip": skip},
                    {"$limit": limit},
                ],
                "pagination": [
                    {"$count": "total"}
                ]
            }
        }
    ]

    lootboxes = lootbox_repository.aggregate(query=query)

    return paginate(lootboxes)


async def activate_lootbox(lootbox_id: str, user_id: int) -> LootBox:
    lootbox = get_lootbox_or_fail(lootbox_id)

    if lootbox.activated:
        raise HTTPException(status_code=409, detail='The lootbox is already activated')

    user_dict = user_service.get_user_or_fail(user_id)

    user = User(**user_dict)

    if lootbox.owner == user.id:
        raise HTTPException(status_code=403, detail="You can't activate your lootbox")

    lootbox_update = LootBoxUpdate(activated=True, user=user.id)
    lootbox_dict = update_lootbox_by_id(lootbox_id, lootbox_update)
    lootbox_updated = lootbox.model_copy(update=lootbox_dict)

    new_points = user.points
    new_balances = {**user.balances}

    for coin_key in lootbox.reward:
        if coin_key == 'points':
            new_points += lootbox.reward[coin_key]
        else:
            if coin_key in new_balances:
                new_balances[coin_key] += lootbox.reward[coin_key]
            else:
                new_balances[coin_key] = lootbox.reward[coin_key]

    user_update_fields = {
        'balances': new_balances,
        'points': new_points
    }

    if not user.referrer:
        user_update_fields['referrer'] = lootbox.owner

        result_referral = await referral_service.create_referral(Referral(**{
            "referrer_id": lootbox.owner,
            "referral_id": user_id
        }))

        if 'error_msg' in result_referral:
            raise HTTPException(status_code=409, detail=result_referral['error_msg'])

    updated_user = UserUpdate(**user_update_fields)
    user_service.update_user_by_user_id(user.id, updated_user)

    try:
        owner_user = User(**user_service.get_user(lootbox.owner))

        await telegram.Bot(token=BOT_TOKEN).send_message(
            chat_id=lootbox.owner,
            text=f'🔔 <b>Your lootbox has been opened by player {user.username_or_name}</b>\n\n' + \
                 f'your balance:\n' + \
                 f'{owner_user.points} <code>$COINs</code> ; {round(owner_user.balances["ton"], 2)} <code>$TON</code> ; {round(owner_user.balances["usdt"], 2)} <code>$USDT</code>\n\n' + \
                 f'Play the game and invite more friends,\n' + \
                 f'yearn more $COINs',
            parse_mode='HTML',
            reply_markup=bot_menu_buttons(owner_user.id)
        )

    except Exception as err:
        print(err)

    return lootbox_updated
