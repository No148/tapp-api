import services.user as user_service
import services.referral as referral_service

from datetime import datetime, timedelta
from fastapi import HTTPException
from config import FARMING_TIME, FARMING_REFERRALS_POINTS, FARMING_SPEED_TIME
from models import User, UserUpdate


def activate_farming(user_id: int) -> UserUpdate:
    user = user_service.get_user_or_fail(user_id)
    max_farm_points = get_farming_max_points(user_id)

    if user['boosters']['auto_farming_boost']['start_farming_date'] and user['boosters']['auto_farming_boost']['finish_farming_date']:
        raise HTTPException(status_code=400, detail='User already activated')

    if max_farm_points <= 0:
        raise HTTPException(status_code=400, detail='You have not enough referrals with taps to activate farming')

    user["boosters"]["auto_farming_boost"] = {
        "start_farming_date": datetime.utcnow(),
        "finish_farming_date": datetime.utcnow() + timedelta(hours=FARMING_TIME),
        "max_farm_points": max_farm_points
    }

    updated_user = User(**user).model_copy(update={"boosters": user["boosters"]})
    user_service.update_user_by_user_id(user_id, updated_user)

    return updated_user


def claim_farming_points(user_id: int) -> UserUpdate:
    user = user_service.get_user_or_fail(user_id)
    max_farm_points = get_farming_max_points(user_id)

    user["boosters"]["auto_farming_boost"] = {
        "start_farming_date": datetime.utcnow(),
        "finish_farming_date": datetime.utcnow() + timedelta(hours=FARMING_TIME),
        "max_farm_points": max_farm_points
    }

    farmed_point = calculate_farming_points(user_id)

    updated_user = User(**user).model_copy(update={"points": user["points"] + round(farmed_point), "boosters": user["boosters"]})

    user_service.update_user_by_user_id(user_id, updated_user)

    return updated_user


def calculate_farming_points(user_id: int):
    user = user_service.get_user_or_fail(user_id)
    user = User(**user)
    farmed_point = 0

    start_farming_date = user.boosters['auto_farming_boost']['start_farming_date']
    finish_farming_date = user.boosters['auto_farming_boost']['finish_farming_date']
    max_farm_points = user.boosters['auto_farming_boost']['max_farm_points']

    if finish_farming_date and datetime.utcnow() >= finish_farming_date:
        farmed_point = max_farm_points

    if finish_farming_date and start_farming_date and finish_farming_date > datetime.utcnow():
        farming_point_in_time = max_farm_points / (FARMING_TIME * FARMING_SPEED_TIME)

        # In seconds
        passed_farming_time = (datetime.utcnow() - start_farming_date).seconds
        farmed_point = int(passed_farming_time) * farming_point_in_time

    return farmed_point


def get_user_farming_data(user_id: int) -> dict:
    user = user_service.get_user_or_fail(user_id)
    max_farm_points = get_farming_max_points(user_id)
    referral_idx = 0

    for key in FARMING_REFERRALS_POINTS:
        if max_farm_points == FARMING_REFERRALS_POINTS[key]:
            referral_idx = key
            break

    user["boosters"]["auto_farming_boost"]["max_farm_points"] = max_farm_points
    updated_user = User(**user).model_copy(update={"boosters": user["boosters"]})

    user_service.update_user_by_user_id(user_id, updated_user)

    return {
        "start_farming_date": user['boosters']['auto_farming_boost']['start_farming_date'],
        "finish_farming_date": user['boosters']['auto_farming_boost']['finish_farming_date'],
        "max_farm_points": max_farm_points,
        "farmed_point": round(calculate_farming_points(user_id)),
        "referral_idx": referral_idx,
    }


def get_farming_max_points(user_id: int) -> int:
    referrals_count = 0
    max_farm_points = 0

    referrals = referral_service.get_referrals_by_params([user_id])

    for referral in referrals:
        if 'raw_taps' in referral and referral['raw_taps'] > 0:
            referrals_count += 1

    if referrals_count in FARMING_REFERRALS_POINTS:
        max_farm_points = FARMING_REFERRALS_POINTS[referrals_count]

    max_referrals_count = max(FARMING_REFERRALS_POINTS.keys())

    if referrals_count >= max_referrals_count:
        max_farm_points = FARMING_REFERRALS_POINTS[max_referrals_count]

    return max_farm_points
