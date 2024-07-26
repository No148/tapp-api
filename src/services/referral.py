import math
import services.user as user_service
import telegram

from bson import ObjectId
from config import REFERRAL_REWARD, REFERRAL_PERCENT_REWARDS, bot_menu_buttons
from models import Referral, UserUpdate, UserReferral, User, ReferralUpdated
from typing import List
from pydantic import TypeAdapter
from repository import ReferralRepository, UserRepository
from services.pagination import paginate
from fastapi import HTTPException
from utils.env import BOT_TOKEN

MAX_REFERRALS_COUNT = 0

user_repository = UserRepository()
referral_repository = ReferralRepository()


def add_accumulated_reward(user: User, original_reward: int, i=1):
    level = f'lvl{i}'

    if level not in REFERRAL_PERCENT_REWARDS:
        return

    user_referrer = user_service.get_user(user.referrer) if user.referrer else None

    if not user_referrer:
        return

    user_referrer = User(**user_referrer)
    user_referrer_referral = get_referral(user.referrer, user.id)

    if not user_referrer_referral:
        return

    calc_reward = float(original_reward * REFERRAL_PERCENT_REWARDS[level] / 100)
    user_referrer_referral.accumulated_reward[level]['available'] += calc_reward

    update_referral_by_id(user_referrer_referral.id, ReferralUpdated(
        accumulated_reward=user_referrer_referral.accumulated_reward
    ))

    add_accumulated_reward(user_referrer, original_reward, i+1)


def pay_referral_reward(referral: Referral) -> dict:
    stored_user = user_service.get_user_or_fail(referral.referrer_id)

    stored_user['points'] = stored_user['points'] + REFERRAL_REWARD

    user_service.update_user_by_user_id(referral.referrer_id, UserUpdate(**stored_user))

    return stored_user


async def create_referral(referral: Referral) -> Referral | dict:
    if check_if_referral_exists(referral.referrer_id, referral.referral_id):
        return {'error_code': 409, 'error_msg': 'Referral already exists'}

    if MAX_REFERRALS_COUNT > 0:
        referrals = get_many_referrals(referral.referrer_id)
        if len(referrals) > MAX_REFERRALS_COUNT:
            return {'error_code': 406, 'error_msg': 'Max amount of Referrals is reached'}

    model_dict = referral.model_dump(exclude=referral.get_excluded_fields())

    referral_repository.create_one(obj=model_dict)

    pay_referral_reward(referral)

    try:
        referer_user = User(**user_service.get_user(referral.referrer_id))
        referral_user = User(**user_service.get_user(referral.referral_id))

        await telegram.Bot(token=BOT_TOKEN).send_message(
            chat_id=referral.referrer_id,
            text=f'🔔 <b>Congrats! You have a new friend joined -</b> {referral_user.username_or_name}\n\n' + \
                 f'your balance:\n' + \
                 f'{referer_user.points} <code>$COINs</code> ; {round(referer_user.balances["ton"], 2)} <code>$TON</code> ; {round(referer_user.balances["usdt"], 2)} <code>$USDT</code>\n\n' + \
                 f'Play the game and invite more friends,\n' + \
                 f'yearn more $COINs',
            parse_mode='HTML',
            reply_markup=bot_menu_buttons(referer_user.id)
        )

    except Exception as err:
        print(err)

    return referral


def get_referrals(skip: int = 0, sort: str = None, limit: int = 100, referrer: int | None = None) -> dict:
    query = [
        {
            "$match": {}
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

    if referrer:
        query[0]['$match']['referrer_id'] = referrer

    referrals = referral_repository.aggregate(query)

    return paginate(referrals)


def check_if_referral_exists(referrer_id: int, referral_id: int) -> bool:
    referral = referral_repository.get_one({
        "referrer_id": referrer_id,
        "referral_id": referral_id
    })

    return bool(referral)


def get_many_referrals(referrer: int | None) -> list[dict]:
    if not referrer:
        return referral_repository.get_many()

    referrals = referral_repository.get_many(
        {"referrer_id": referrer}
    )

    return TypeAdapter(list[dict]).validate_python(referrals)


def get_referrals_by_user_id(user_id: int, skip: int = 0, sort: str = None, limit: int = 100) -> dict:
    formatted_user_referrals = []

    referrals = get_referrals(skip=skip, sort=sort, limit=limit, referrer=user_id)
    user_referrals = get_referrals_by_params(user_ids=[user_id])

    for referral in referrals['items']:
        referral = Referral(**referral)

        for user_referral in user_referrals:
            user_referral = UserReferral(**user_referral)

            if referral.referral_id == user_referral.id and user_id == referral.referrer_id:
                user_referral.reward = referral.reward
                user_referral.accumulated_reward_available = referral.accumulated_reward_available
                user_referral.accumulated_reward_received = referral.accumulated_reward_received
                user_referral.accumulated_rewards = referral.accumulated_reward
                formatted_user_referrals.append(user_referral)

    referrals['items'] = formatted_user_referrals

    return {
        'referrals': formatted_user_referrals,
        'percent_rewards': REFERRAL_PERCENT_REWARDS,
        'total_count': referrals['total_count'] if 'total_count' in referrals else 0
    }


def get_referrals_accumulated_rewards(user_id: int) -> dict:
    referrals = get_many_referrals(referrer=user_id)
    accumulated = {}
    available_sum = 0
    received_sum = 0

    for referral in referrals:
        referral = Referral(**referral)

        for lvl, accumulated_reward in referral.accumulated_reward.items():
            if lvl not in accumulated:
                accumulated[lvl] = {**accumulated_reward}
            else:
                for key, val in accumulated_reward.items():
                    accumulated[lvl][key] += val

            available_sum += accumulated_reward['available']
            received_sum += accumulated_reward['received']

    available_sum = math.floor(available_sum)

    return {
        'accumulated': accumulated,
        'available_sum': available_sum,
        'received_sum': received_sum,
        'percent_rewards': REFERRAL_PERCENT_REWARDS
    }


def get_referrals_by_params(user_ids: [int] = None) -> list[dict]:
    if not user_ids:
        user_ids = []

    if len(user_ids) > 0:
        users = user_repository.get_many({"referrer": {"$in": user_ids}})

        return TypeAdapter(list[dict]).validate_python(users)

    return []


def get_multilevel_referrals_for_user(user_tg_id: int, deep_level: int = 1) -> dict:
    multi_level_referrals = {}
    taps_by_levels = {}
    prev_level = None

    if not bool(user_service.get_user(user_tg_id)):
        raise HTTPException(status_code=404, detail=f'User with telegram id: {user_tg_id} does not exist')

    for lvl in range(0, deep_level):
        lvl += 1

        ta = TypeAdapter(List[User])

        if prev_level:
            referrer_ids = [referrer.id for referrer in multi_level_referrals[prev_level]]
            referrals = get_referrals_by_params(user_ids=referrer_ids)
        else:
            referrals = get_referrals_by_params(user_ids=[user_tg_id])

        if referrals:
            multi_level_referrals[lvl] = ta.validate_python(referrals)
            prev_level = lvl

        taps_by_levels = {}

        for level in multi_level_referrals:
            taps_by_levels[level] = {}
            taps_by_levels[level]['total_taps'] = 0

            for user in multi_level_referrals[level]:
                taps_by_levels[level]['total_taps'] += int(user.taps)

    return {
        'users_by_levels': multi_level_referrals,
        'taps_by_levels': taps_by_levels
    }


def get_referral(referrer_id: int, referral_id: int) -> Referral:
    referral_dict = referral_repository.get_one(
        query={
            'referrer_id': referrer_id,
            'referral_id': referral_id,
        }
    )

    return Referral(**referral_dict) if referral_dict else None


def get_referral_or_fail(referrer_id: int, referral_id: int) -> Referral:
    referral = get_referral(referrer_id, referral_id)

    if not referral:
        raise HTTPException(status_code=404, detail='Referral not found')

    return referral


def update_referral_by_id(referral_id: str, model_update: ReferralUpdated) -> dict:
    model_update_dict = model_update.model_dump(exclude_unset=True, exclude=model_update.get_excluded_fields())

    referral_repository.update_one(
        query={"_id": ObjectId(referral_id)},
        update={
            '$set': model_update_dict
        }
    )

    return model_update_dict
