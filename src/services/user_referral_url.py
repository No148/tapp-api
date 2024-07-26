import random
import services.user as user_service
import services.project as project_service

from fastapi import HTTPException
from models import UserReferralUrl, Project
from bson import ObjectId
from repository import UserReferralUrlRepository, ProjectRepository
from services.pagination import paginate
from config import EXCLUDE_PROJECTS


user_referral_url_repository = UserReferralUrlRepository()
project_repository = ProjectRepository()


async def get_user_referral_urls(skip: int = 0, sort: str = None, limit: int = 50, user_tg_id: int = None, is_valid: bool = None) -> dict:
    query = {}

    if user_tg_id:
        query["user_tg_id"] = user_tg_id

    if is_valid is not None:
        query["is_valid"] = is_valid

    result = user_referral_url_repository.get_user_referral_urls(query=query, limit=limit, sort=sort, skip=skip)

    return paginate(result)


async def create_user_referral_url(user_referral_url: UserReferralUrl, is_parse_metadata: bool = True, is_validate_only: bool = False) -> UserReferralUrl | dict:
    message_err_invalid_reff_url = 'Invalid provided referral url. Examples: t.me/MyApp_Bot?start=r2354732; https://t.me/myappbot?startapp=r2354732'
    min_characters_in_url = 11

    if not user_referral_url.url or len(user_referral_url.url) < min_characters_in_url:
        raise HTTPException(status_code=400, detail=message_err_invalid_reff_url)

    if any(exclude_project in user_referral_url.url for exclude_project in EXCLUDE_PROJECTS):
        raise HTTPException(status_code=400, detail='Sorry, current bot can not be added')

    user_referral_url.url = user_referral_url.url.lower()

    if not any(vsu in user_referral_url.url for vsu in ['http://', 'https://']):
        if user_referral_url.url[:5] == 't.me/':
            user_referral_url.url = 'https://' + user_referral_url.url
        else:
            raise HTTPException(status_code=400, detail=message_err_invalid_reff_url)

    project_url = None

    splited_ref_url = user_referral_url.url.split('/')

    if len(splited_ref_url) >= 4:
        project_url = splited_ref_url[0] + '//' + splited_ref_url[2]

        splited_ref_url = splited_ref_url[3].split('?')

        if len(splited_ref_url) >= 1:
            project_url += '/' + splited_ref_url[0]
    else:
        splited_ref_url = []

    is_bot_ref_url = splited_ref_url[0].endswith("bot") if len(splited_ref_url) >= 1 else False

    validate_start_url = ['t.me/']
    validate_params = ['?start=', '?startapp=', '?appstart=']

    if not user_referral_url.url or not is_bot_ref_url \
            or not any(vsu in user_referral_url.url for vsu in validate_start_url) \
            or not any(vp in user_referral_url.url for vp in validate_params):
        raise HTTPException(status_code=400, detail=message_err_invalid_reff_url)

    user = user_service.get_user(user_id=user_referral_url.user_tg_id)

    if not user:
        raise HTTPException(status_code=400, detail=f'User with telegram id: {user_referral_url.user_tg_id} does not exist')

    if user_referral_url_repository.check_if_user_referral_url_exist(user_referral_url.user_tg_id, user_referral_url.url):
        raise HTTPException(status_code=400, detail='User referral url already exists')

    project = None

    if project_url:
        if is_parse_metadata:
            project = await project_service.create_project(Project(**{'url': project_url}))
        else:
            project = project_repository.get_one({"url": {"$regex": project_url, "$options": "i"}})

    if is_validate_only:
        return {"is_valid": True}

    if project:
        user_referral_url.project_id = ObjectId(project.id)

        if hasattr(project, 'is_valid'):
            user_referral_url.is_valid = project.is_valid

    user_referral_url_dict = user_referral_url.model_dump(exclude=user_referral_url.get_excluded_fields())
    user_referral_url = user_referral_url_repository.create_one(user_referral_url_dict)

    if project:
        user_referral_url['project'] = project.model_dump(by_alias=True)

    return UserReferralUrl(**user_referral_url)


def get_random_referral_urls(exclude_ids='', exclude_project_urls='', random_count=5) -> list[dict]:
    query = {}

    if exclude_ids and exclude_ids.strip() != '':
        exclude_ids = exclude_ids.lower()

        exclude_ids = [ObjectId(exclude_id) for exclude_id in exclude_ids.split(',')]

        query['_id'] = {"$nin": exclude_ids}

    if exclude_project_urls and exclude_project_urls.strip() != '':
        exclude_project_urls = exclude_project_urls.lower()

        project_urls = exclude_project_urls.split(',')

        query["$and"] = []

        for project_url in project_urls:
            if project_url.find('?') >= 0:
                project_url = project_url[:project_url.index("?")]

            query["$and"].append({"url": {"$not": {"$regex": project_url, "$options": 'i'}}})

    user_referral_urls = paginate(user_referral_url_repository.get_user_referral_urls(query=query, sort={'referrer_count': 1}))
    user_referral_urls = user_referral_urls['items']

    ref_urls_by_projects = {}

    for user_referral_url in user_referral_urls:
        if 'project' in user_referral_url and user_referral_url['project']:
            if user_referral_url['project']['_id'] not in ref_urls_by_projects:
                ref_urls_by_projects[user_referral_url['project']['_id']] = user_referral_url

    if random_count > len(ref_urls_by_projects.keys()):
        random_count = len(ref_urls_by_projects.keys())

    random_referral_urls = random.sample(list(ref_urls_by_projects), random_count) if len(ref_urls_by_projects.keys()) > 0 else []

    return [ref_urls_by_projects[key] for key in random_referral_urls]


def increase_referrer_count(_id: str) -> UserReferralUrl | dict:
    query = {}

    if not _id or _id.strip() == '':
        return {'error_code': 400, 'error_msg': f'Incorrect data to increase referrer count: {_id}'}

    _id = ObjectId(_id)

    query['_id'] = _id

    user_referral_url = user_referral_url_repository.get_one(query)

    user_referral_url['referrer_count'] += 1

    user_referral_url_repository.update_one(
        query=query,
        update={"$set": {'referrer_count': user_referral_url['referrer_count']}}
    )

    return user_referral_url


def validate_by_project_id(project_id: str, is_valid: bool):
    return user_referral_url_repository.update_many({"project_id": ObjectId(project_id)}, {"is_valid": is_valid})
