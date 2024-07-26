import datetime
import services.user as user_service

from fastapi import HTTPException
from config import BOOSTERS, BOOST_PRICE_CHANGER
from models import Boost, User, UserUpdate
from .boost_purchase import create_boost_purchase, check_if_boost_purchase_exist
from bson import ObjectId


def get_interval_booster_config_by_key(key: str) -> bool | dict:
    boosters_cfg = BOOSTERS

    for booster in boosters_cfg['interval']:
        for booster_key, booster_cfg in booster.items():
            if booster_key == key:
                return booster_cfg

    return False


def calculate_boost_next_level(boost_price_changer, user_booster) -> dict:

    # Condition to reset price step and recycling price up with level up
    if user_booster["price_step"] > len(boost_price_changer):
        user_booster["price_step"] = 1

    for price_changer in boost_price_changer:
        if price_changer["step"] == user_booster["price_step"]:

            # Set current_level_price value from next_level_price to calculate on it price for next_level_price with price_step value
            user_booster["current_level_price"] = int(user_booster["next_level_price"])

            # Check if step change price using factor
            if "factor" in price_changer:
                user_booster["next_level_price"] = int(user_booster["current_level_price"] * price_changer["factor"])

            # Check if step change price using percent
            if "percent" in price_changer:
                user_booster["next_level_price"] = int(user_booster["current_level_price"] + ((user_booster["current_level_price"] * price_changer["percent"]) / 100))

            # Check if step change price using sum
            if "sum" in price_changer:
                user_booster["next_level_price"] = int(user_booster["current_level_price"] + price_changer["sum"])

            # Increment price step to next time calculate price with another condition
            user_booster["price_step"] += 1

            # Level up
            user_booster["current_level"] = user_booster["next_level"]
            user_booster["next_level"] += 1

            break

    return user_booster


async def boost_purchase(boost: Boost) -> UserUpdate:
    stored_user = User(**user_service.get_user_or_fail(boost.user_id))

    if boost.boost not in stored_user.boosters:
        raise HTTPException(status_code=400, detail='Incorrect boost')

    user_booster = stored_user.boosters[boost.boost]

    if check_if_boost_purchase_exist(stored_user.id, boost.boost, (stored_user.boosters[boost.boost]['current_level'] + 1)):
        raise HTTPException(status_code=409, detail='Boost purchase already exists')

    # Subtract price for boost from users points
    stored_user = user_service.subtract_points(stored_user, user_booster)

    # Calculate next boost level for users
    next_level = calculate_boost_next_level(BOOST_PRICE_CHANGER[boost.boost], user_booster)

    stored_user.boosters[boost.boost] = next_level

    create_boost_purchase({
            "user_tg_id": stored_user.id,
            "user_id": ObjectId(stored_user.storage_id),
            "boost": boost.boost,
            "level": next_level['current_level'],
            "price": next_level['current_level_price'],
            "created_at": datetime.datetime.utcnow()
        })

    user_service.update_user_by_user_id(stored_user.id, stored_user)

    return stored_user
