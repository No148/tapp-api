import services.user as user_service
import services.project as project_service
import telegram

from datetime import datetime, timedelta
from fastapi import HTTPException
from bson import ObjectId
from config import TASK_CONFIRMATION_MINUTES, USER_LEVELS, DAILY_TASK_REWARDS, ACCOUNT_AGE_PER_YEAR_REWARD
from models import TaskBounty, User
from utils.env import BOT_TOKEN
from utils.helper import get_age_of_account_by_user_id
from .helper import check_object_id
from repository import TaskBountyRepository
from services.pagination import paginate

task_bounty_repository = TaskBountyRepository()


def create_one_task_bounty(task: dict) -> dict:
    return task_bounty_repository.create_one(task)


def get_one_task_bounty(task_bounty_id: str) -> dict:
    return task_bounty_repository.get_one({'_id': ObjectId(task_bounty_id)})


async def get_user_task_bounties_by_id(user_id: int, skip: int = 0, sort: str = None, limit: int = 50) -> dict:
    stored_user = user_service.get_user_or_fail(user_id)
    user = User(**stored_user)
    task_bounties = paginate(task_bounty_repository.get_task_bounties({}, skip, sort, limit))

    user_tasks = {task['_id']: task for task in stored_user['tasks']}
    user_referral_count = user_service.get_referral_count(stored_user['id'])

    for index, task_bounty in enumerate(task_bounties['items']):
        task_bounty_id = str(task_bounty['_id'])

        if task_bounty['type'] in ['ref', 'league']:
            if task_bounty['type'] == 'ref':
                task_bounty['progress'] = user_referral_count / task_bounty['required_number_of_referrals'] * 100

            elif task_bounty['type'] == 'league':
                task_bounty['progress'] = stored_user['taps'] / USER_LEVELS[task_bounty['league_level_index']]['taps'] * 100

            task_bounty['progress'] = round(task_bounty['progress'], 2)
            task_bounty['progress'] = min(100, task_bounty['progress'])

            if task_bounty['progress'] >= 100:
                task_bounty['status'] = 'claimable'

        elif task_bounty['type'] == 'daily_reward':
            task_bounty['daily_rewards'] = DAILY_TASK_REWARDS
            task_bounty['progress'] = user.daily_reward_progress
            task_bounty['status'] = 'claimable' if user.daily_reward_available else 'done'

        elif task_bounty['type'] == 'age_of_account':
            task_bounty['account_age'] = get_age_of_account_by_user_id(user.id)
            task_bounty['reward'] = task_bounty['account_age'] * ACCOUNT_AGE_PER_YEAR_REWARD
            task_bounty['reward_per_year'] = ACCOUNT_AGE_PER_YEAR_REWARD

        if task_bounty_id in user_tasks:
            user_task = user_tasks[task_bounty_id]

            task_bounty['started_at'] = user_task['started_at']
            task_bounty['claimed'] = user_task['claimed']

            if 'lang' in user_task and user_task['lang']:
                task_bounty['lang'] = user_task['lang']

            if user_task['claimed']:
                task_bounty['status'] = 'done'
            else:
                if task_bounty['type'] == 'social':
                    if 'action_checker' not in task_bounty and user_task['started_at'] and datetime.utcnow() > user_task['started_at'] + timedelta(minutes=TASK_CONFIRMATION_MINUTES):
                        task_bounty['status'] = 'claimable'

                    elif user_task['started_at']:
                        action_success = await action_checker_processing(TaskBounty(**task_bounty), user_id)

                        if action_success:
                            await user_service.claim_task_bounty(user_id, task_bounty_id)
                            user_task['claimed'] = True
                            task_bounty['status'] = 'done'
                        else:
                            task_bounty['status'] = 'processing'

                elif task_bounty['type'] == 'add_project':
                    if user_task['started_at']:
                        task_bounty['status'] = 'processing'

                        project = project_service.get_project(user_task['project_id'])
                        
                        task_bounty['project_id'] = None
                        task_bounty['project'] = {}

                        if project:
                            task_bounty['project_id'] = project.id
                            task_bounty['project'] = project.model_dump()

                            if project.is_valid: 
                                task_bounty['status'] = 'claimable'

                elif task_bounty['type'] == 'age_of_account':
                    task_bounty['reward'] = user_task['reward']
                    task_bounty['status'] = 'claimable'

        task_bounties['items'][index] = task_bounty

    return task_bounties


async def create_task_bounty(task: TaskBounty) -> TaskBounty:
    return create_one_task_bounty(dict(task))


async def get_task_bounties(skip: int = 0, sort: str = None, limit: int = 50) -> dict:
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

    task_bounties = task_bounty_repository.aggregate(query)

    return paginate(task_bounties)


def get_task_bounty(task_bounty_id: str) -> dict:
    check_object_id(task_bounty_id)
    result = task_bounty_repository.get_one({'_id': ObjectId(task_bounty_id)})

    if not result:
        raise HTTPException(status_code=404, detail='Task not found')

    return result


async def action_checker_processing(task_bounty: TaskBounty, user_id: int) -> bool:
    try:
        if not task_bounty.action_checker:
            return False

        if task_bounty.action_checker == 'telegram_join' and task_bounty.lang:
            chat_member = await telegram.Bot(token=BOT_TOKEN).get_chat_member(
                chat_id=task_bounty.action_data[task_bounty.lang]['id'], user_id=user_id)

            return chat_member.status != 'left'

        elif task_bounty.action_checker == 'telegram_boost':
            chat_boost = await telegram.Bot(token=BOT_TOKEN).get_user_chat_boosts(
                chat_id=task_bounty.action_data['channel_id'], user_id=user_id)

            return len(chat_boost.boosts) > 0
    except Exception as err:
        print(err)
        pass

    return False
