import math
import urllib.parse
import telegram
import services.boost as boost_service
import services.referral as referral_service
import services.lootbox as lootbox_service
import services.project as project_service

from decimal import *
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from config import REFERRAL_REWARD, BOOSTERS, TAPPING_GURU, MINIMUM_CLAIM_ACCUMULATED_REWARD, DAILY_TASK_REWARDS, ACCOUNT_AGE_PER_YEAR_REWARD
from models import UserUpdate, User, Referral, Project, ReferralUpdated
from utils.helper import get_age_of_account_by_user_id
from .task_bounty import get_task_bounty
from utils.env import BOT_USERNAME, BOT_TOKEN
from utils.logger import logger
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from repository import UserRepository, ReferralRepository
from services.pagination import paginate

user_repository = UserRepository()
referral_repository = ReferralRepository()


async def create_user(user: User):
    create_one_user(dict(user))

    return user


def get_user(user_id: int) -> dict:
    return user_repository.get_one(query={"id": user_id})


def update_user_by_user_id(user_id: int, updated_user: UserUpdate) -> dict:
    user_dict = updated_user.model_dump(
        exclude_unset=True,
        exclude=updated_user.get_excluded_fields()
    )
    return user_repository.update_one(
        query={"id": user_id},
        update={"$set": user_dict}
    )


def create_one_user(user: dict):
    return user_repository.create_one(obj=user)


def get_user_or_fail(user_id: int) -> dict:
    user = get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


async def get_user_by_id(user_id: int) -> dict:
    return get_user_or_fail(user_id)


def update_user(user_id: int, user: UserUpdate) -> UserUpdate:
    stored_user = get_user_or_fail(user_id)
    updated_user = User(**stored_user).model_copy(update=user.model_dump(exclude_unset=True))
    updated_user.updated_at = datetime.utcnow()

    update_user_by_user_id(user_id, updated_user)

    return updated_user


def add_to_favorite_projects(user_id: int, project_id: str):
    return user_repository.update_one(
        query={'id': user_id},
        update={
            "$set": {f"favorite_projects.{project_id}": {"last_opened_date": None}}
        }
    )


async def add_task_bounty(user_id: int, task_bounty_id: str, body=None) -> UserUpdate:
    if not body:
        body = {}

    stored_user = get_user_or_fail(user_id)
    task_bounty = get_task_bounty(task_bounty_id)

    for idx, task in enumerate(stored_user['tasks']):
        if task['_id'] == task_bounty_id and task_bounty['type'] != 'add_project':
            raise HTTPException(status_code=409, detail='Task Bounty already exists')

    new_task = {
        '_id': str(task_bounty['_id']),
        'title': task_bounty['title'],
        'reward': task_bounty['reward'] if 'reward' in task_bounty else None,
        'claimed': False,
        'active': task_bounty['active'],
        'started_at': datetime.utcnow()
    }
    
    if task_bounty['type'] == 'add_project':
        if not body or 'project_url' not in body or not body['project_url']:
            raise HTTPException(status_code=400, detail='Empty body or project_url')
        
        project_url = body['project_url']

        if project_service.check_on_exist_project_by_url_regex(project_url):
            raise HTTPException(status_code=400, detail='Project with provided url already exists')
        
        project_exist = None
        found_task_idx = None

        for idx, task in enumerate(stored_user['tasks']):
            task_exist = True if task['_id'] == task_bounty_id else False
            project_exist = project_service.get_project(task['project_id']) if task_exist else None

            if task_exist:
                found_task_idx = idx
                break

        if project_exist and project_exist.is_valid is False:
            new_project: Project = await project_service.create_project(Project(**{'url': project_url}))
            
            stored_user['tasks'][found_task_idx]['project_id'] = new_project.id

            updated_user = User(**stored_user).model_copy(update={
                'tasks': stored_user['tasks']
            })

            update_user_by_user_id(user_id, updated_user)

            return updated_user 
        elif project_exist and project_exist.is_valid:
            raise HTTPException(status_code=409, detail='Project already submitted and was approved')
        elif project_exist and project_exist.is_valid is None:
            raise HTTPException(status_code=409, detail='Project already submitted and is in moderation')
        elif not project_exist:
            new_project: Project = await project_service.create_project(Project(**{'url': project_url}))
            new_task['project_id'] = new_project.id

    elif task_bounty['type'] == 'age_of_account':
        account_age = get_age_of_account_by_user_id(user_id)
        new_task['reward'] = account_age * ACCOUNT_AGE_PER_YEAR_REWARD
        new_task['account_age'] = account_age

    if 'action_checker' in task_bounty and task_bounty['action_checker'] == 'telegram_join':
        possible_langs = ['en', 'ru']

        if not body or 'lang' not in body or not body['lang'] or body['lang'] not in possible_langs:
            raise HTTPException(status_code=400, detail='Empty body or lang param')

        new_task['lang'] = body['lang']
    
    updated_user = User(**stored_user).model_copy(update={
        'tasks': stored_user['tasks'] + [new_task]
    })

    update_user_by_user_id(user_id, updated_user)

    return updated_user


async def claim_task_bounty(user_id: int, task_bounty_id: str) -> UserUpdate:
    task_bounty = get_task_bounty(task_bounty_id)

    if task_bounty['type'] in ['ref', 'league']:
        try:
            await add_task_bounty(user_id, task_bounty_id)
        except HTTPException as err:
            if err.status_code == 409:
                print(err)
            else:
                raise HTTPException(status_code=err.status_code, detail=err.detail)
        except Exception as err:
            raise err

    stored_user = get_user_or_fail(user_id)
    user_task = None

    for idx, task in enumerate(stored_user['tasks']):
        if task['_id'] == task_bounty_id:
            user_task = task

            if 'claimed' in task and task['claimed']:
                raise HTTPException(status_code=409, detail='Task Bounty already claimed')

            stored_user['tasks'][idx]['claimed'] = True

    if not user_task:
        raise HTTPException(status_code=400, detail='User has not task to claim')

    updated_user = User(**stored_user).model_copy(update={
        'points': stored_user['points'] + user_task['reward'],
        'tasks': stored_user['tasks']
    })

    update_user_by_user_id(user_id, updated_user)

    return updated_user


async def claim_daily_reward_task(user_id: int) -> UserUpdate:
    user = User(**get_user_or_fail(user_id))

    if not user.daily_reward_available:
        raise HTTPException(status_code=400, detail="You can't get an reward yet")

    if user.daily_reward_progress not in DAILY_TASK_REWARDS:
        raise HTTPException(status_code=400, detail='No daily progress')

    reward = DAILY_TASK_REWARDS[user.daily_reward_progress]

    update_fields = {
        'daily_reward_available': False,
        'points': user.points + reward
    }

    update_user_by_user_id(user_id, UserUpdate(**update_fields))

    return user.model_copy(update=update_fields)


async def add_points(user_id: int, user: UserUpdate) -> User:
    stored_user = get_user_or_fail(user_id)

    user_repository.update_one(
        query={"id": user_id},
        update={
            "$inc": {
                'points': user.points
            }
        }
    )

    stored_user['points'] += user.points

    return User(**stored_user)


def add_points_lite(user_id: int, points: int) -> bool:
    user_repository.update_one(
        query={"id": user_id},
        update={
            "$inc": {
                'points': points
            }
        }
    )

    return True


async def add_taps(user_id: int, user_update: UserUpdate) -> UserUpdate:
    refilled_energy = 0
    taping_guru_is_active = False
    stored_user = User(**get_user_or_fail(user_id))
    taps = user_update.taps * stored_user.tap_power
    tapping_started_date = user_update.tapping_started_date

    if tapping_started_date:
        seconds_from_tap_start = (datetime.utcnow().replace(tzinfo=timezone.utc) - tapping_started_date).total_seconds()
        seconds_from_tap_start -= 1
        if seconds_from_tap_start < 0:
            seconds_from_tap_start = 0
        refilled_energy = round(seconds_from_tap_start * stored_user.recharging_speed)

    if taps < 0:
        raise HTTPException(status_code=400, detail='Taps must be positive integer')

    energy_left = stored_user.energy + refilled_energy - taps

    if (
        stored_user.calculated_interval_boosters['tapping_guru']['expiry_date'] and
        datetime.utcnow() < stored_user.calculated_interval_boosters['tapping_guru']['expiry_date'] + timedelta(seconds=3)
    ):
        taping_guru_is_active = True
        # tmp until better option to save last taping guru taps portion
        if not stored_user.taping_guru_is_active:
            taps = user_update.taps * stored_user.tap_power * TAPPING_GURU['taps_multiplier']

        energy_left = stored_user.energy

    print(f'Raw taps: {user_update.taps}, taps: {taps}, stored_energy: {stored_user.energy}, refilled_energy: {refilled_energy}, energy_left: {energy_left}')

    if not taping_guru_is_active and energy_left < 0:
        raise HTTPException(status_code=400, detail='Not enough energy')

    referral_service.add_accumulated_reward(stored_user, taps)

    updated_user = stored_user.model_copy(update={
        'raw_taps': stored_user.raw_taps + user_update.taps,
        'taps': stored_user.taps + taps,
        'points': stored_user.points + taps,
        'energy_last_use': {
            'energy': energy_left,
            'date': datetime.utcnow()
        }
    })

    if stored_user.raw_taps == 0 and stored_user.referrer is not None:
        updated_user.points = updated_user.points + REFERRAL_REWARD

    update_user_by_user_id(user_id, updated_user)

    return updated_user


async def get_user_boosters_by_id(user_id: int) -> dict:
    stored_user = User(**get_user_or_fail(user_id)).model_dump()
    boosters_cfg = BOOSTERS
    response = {
        'available_points': stored_user['points'],
        'interval': [],
        'purchasable': []
    }

    for booster in boosters_cfg['purchasable']:
        for booster_key, booster_cfg in booster.items():
            response['purchasable'].append({
                'key': booster_key,
                'title': booster_cfg['title'],
                'description': booster_cfg['description'],
                'level': stored_user['boosters'][booster_key]['current_level'],
                'next_level': stored_user['boosters'][booster_key]['next_level'],
                'next_price': stored_user['boosters'][booster_key]['next_level_price'],
                'next_level_available': True if stored_user['points'] >= stored_user['boosters'][booster_key]['next_level_price'] else False
            })

    for booster in boosters_cfg['interval']:
        for booster_key, booster_cfg in booster.items():
            pre_data = {
                'key': booster_key,
                'title': booster_cfg['title'],
                'description': booster_cfg['description'],
                'max_amount': booster_cfg['max_amount'],
                'interval_hours': booster_cfg['interval_hours']
            }

            if 'duration_seconds' in booster_cfg:
                pre_data['duration_seconds'] = booster_cfg['duration_seconds']

            pre_data = pre_data | stored_user['calculated_interval_boosters'][booster_key]

            response['interval'].append(pre_data)

    return response


async def bot_send_invite_friends(user_id: int) -> bool:
    try:
        ref_link = f'https://t.me/{BOT_USERNAME}?start={user_id}'

        await telegram.Bot(token=BOT_TOKEN).send_message(
            chat_id=user_id,
            text=f'Invite friend and get {REFERRAL_REWARD} coins!',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text='Press here to share with friends',
                        url=f"https://t.me/share/url?url={urllib.parse.quote(ref_link, safe='')}&text={urllib.parse.quote(f'🎁 +{REFERRAL_REWARD} Coins as a first-time gift')}"
                    )
                ],
                [
                    InlineKeyboardButton(text='× Hide', callback_data='delete')
                ]
            ])
        )

    except Exception as err:
        logger.error(err)
        return False

    return True


def subtract_points(stored_user: User, user_booster) -> User:
    if user_booster["next_level_price"] > stored_user.points:
        raise HTTPException(status_code=400, detail='Can not subtract more then exist points')

    stored_user.points -= user_booster["next_level_price"]
    stored_user.spent_points += user_booster["next_level_price"]
    
    update_user_by_user_id(stored_user.id, stored_user)

    return stored_user


async def get_or_upsert_user(user: User) -> User:
    user_model: User
    stored_user = get_user(user.id)

    if stored_user:
        user_model = User(**stored_user)

        if user.referrer and (stored_user['referrer'] or not get_user(user.referrer)):
            delattr(user, 'referrer')

        utcnow = datetime.utcnow()
        user.last_login_date = utcnow

        if user_model.last_login_date.date() != utcnow.date():
            if (
                (utcnow.date() - user_model.last_login_date.date()).days == 1 and
                user_model.daily_reward_progress < max(list(DAILY_TASK_REWARDS.keys())) and
                not user.daily_reward_available
            ):
                user.daily_reward_progress = user_model.daily_reward_progress + 1
            else:
                user.daily_reward_progress = 1

            user.daily_reward_available = True

        update_fields = user.model_dump(exclude_unset=True, exclude=user.get_excluded_fields())
        user_update = UserUpdate(**update_fields)
        update_user_by_user_id(stored_user['id'], user_update)
        user_model = User(**stored_user).model_copy(update=update_fields)

    else:
        if user.referrer and not get_user(user.referrer):
            user.referrer = None

        create_fields = user.model_dump(exclude=user.get_excluded_fields())
        user_model = User(**create_one_user(create_fields))

        lootbox_service.generate_and_create_lootbox(user.id)

    if user_model.referrer and (not stored_user or not stored_user['referrer']):
        result_referral = await referral_service.create_referral(Referral(**{
            "referrer_id": user.referrer,
            "referral_id": user.id
        }))

        if 'error_msg' in result_referral:
            logger.info(result_referral['error_msg'])

    # Check if user exist task with type "age_of_account", if not then added task to user

    finding_task_account_age = False

    for task in user_model.tasks:
        if task['_id'] == '66a03a8bf14e5938fd66d8e2':
            finding_task_account_age = True
            break

    if not finding_task_account_age:
        await add_task_bounty(user.id, '66a03a8bf14e5938fd66d8e2')
        user_model = User(**get_user(user.id))

    return user_model


async def activate_interval_booster(user_id: int, interval_booster_key: str) -> bool:
    stored_user = User(**get_user_or_fail(user_id)).model_dump()
    interval_booster_cfg = boost_service.get_interval_booster_config_by_key(interval_booster_key)

    if not interval_booster_cfg:
        return False

    user_interval_boosters = stored_user['calculated_interval_boosters']

    if user_interval_boosters[interval_booster_key]['amount'] <= 0:
        return False

    user_interval_boosters[interval_booster_key]['amount'] -= 1

    if 'duration_seconds' in interval_booster_cfg:
        user_interval_boosters[interval_booster_key]['expiry_date'] = datetime.utcnow() + timedelta(seconds=interval_booster_cfg['duration_seconds'])

    if user_interval_boosters[interval_booster_key]['amount'] == 0:
        user_interval_boosters[interval_booster_key]['recovery_date'] = datetime.utcnow() + timedelta(hours=interval_booster_cfg['interval_hours'])

    user_update_fields = {
        'interval_boosters': user_interval_boosters
    }

    if interval_booster_key == 'energy_refresh':
        if 'energy_last_use' in stored_user and 'date' in stored_user['energy_last_use']:
            user_update_fields['energy_last_use'] = stored_user['energy_last_use']
            del user_update_fields['energy_last_use']['date']

    update_user_by_user_id(user_id, User(**stored_user).model_copy(update=user_update_fields))

    return True


def get_referral_count(user_id: int) -> int:
    return referral_repository.count_documents(
        {"referrer_id": user_id}
    )


def referrals_claim_accumulated_reward(user_id: int) -> bool:
    referrals = referral_service.get_many_referrals(referrer=user_id)
    available_sum = 0

    for referral in referrals:
        referral = Referral(**referral)

        for level in referral.accumulated_reward:
            available_sum += referral.accumulated_reward[level]['available']

    available_sum = math.floor(available_sum)

    if available_sum < MINIMUM_CLAIM_ACCUMULATED_REWARD:
        return False

    for referral in referrals:
        referral = Referral(**referral)

        for level in referral.accumulated_reward:
            available = math.floor(referral.accumulated_reward[level]['available'])

            referral.accumulated_reward[level]['received'] = available
            referral.accumulated_reward[level]['available'] = float(Decimal(str(referral.accumulated_reward[level]['available'])) - Decimal(str(available)))

        referral_service.update_referral_by_id(referral.id, ReferralUpdated(
            accumulated_reward=referral.accumulated_reward
        ))

    add_points_lite(user_id, available_sum)

    return True


def get_leaderboard(user_id: int = None, sort: str = None, limit: int = 250) -> dict:
    sort_dict = {sort[1:]: -1} if sort[0] == '-' else {sort[0:]: 1}

    result = paginate(user_repository.get_leaderboard(sort=sort_dict, skip=0, limit=limit))

    if user_id:
        user = get_user(user_id)

        if user:
            user = User(**user)

            if not any(user.id == leader["id"] for leader in result['items']):
                referrals = referral_service.get_referrals_by_params([user_id])

                current_user_leaderboard = {
                    "_id": user.storage_id,
                    "id": user.id,
                    "taps": user.taps,
                    "raw_taps": user.raw_taps,
                    "points": user.points,
                    "level_info": user.level_info,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "referrals_count": len(referrals)
                }

                result['items'].append(current_user_leaderboard)

                sort_direction = True if sort[0] == '-' else False
                sort_field = sort[1:] if sort[0] == '-' else sort

                if sort in current_user_leaderboard:
                    result['items'].sort(key=lambda x: x[sort_field] if sort_field in x else 0, reverse=sort_direction)

    return result['items']
