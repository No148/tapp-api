import datetime

from fastapi import HTTPException
from models import UserUpdate
from bson import ObjectId
from repository import ProjectRepository
from services.pagination import paginate
from services.helper import check_object_id
from services.project import check_on_exist_project

import services.user as user_service

project_repository = ProjectRepository()


def add_project(user_id: int, body: dict) -> list:
    if 'project_id' not in body:
        raise HTTPException(status_code=400, detail='Required "project_id" field')

    check_object_id(body['project_id'])

    if not check_on_exist_project(project_id=body['project_id']):
        raise HTTPException(status_code=404, detail='Project does not exist')

    user_update = UserUpdate(**user_service.get_user_or_fail(user_id))

    project_id = body['project_id']

    if user_update.favorite_projects and project_id in user_update.favorite_projects:
        raise HTTPException(status_code=400, detail="Project already in favorites")

    user_update.favorite_projects[project_id] = {"last_opened_date": None}

    user_service.add_to_favorite_projects(user_id, body['project_id'])

    return [str(project_id) for project_id in user_update.favorite_projects]


def delete_project(user_id: int, _id: str) -> list:
    check_object_id(_id)

    user = user_service.get_user_or_fail(user_id)
    user_update = UserUpdate(**user)

    if _id not in user_update.favorite_projects:
        raise HTTPException(status_code=400, detail="Project does not exist in favorites")

    del user_update.favorite_projects[_id]

    user_service.update_user_by_user_id(user_id, user_update)

    return [str(project_id) for project_id in user_update.favorite_projects]


def get_projects(user_id: int, sort: str, limit: int, offset: int) -> dict:
    user = user_service.get_user_or_fail(user_id)

    if 'favorite_projects' not in user or not user['favorite_projects'] or len(user['favorite_projects']) <= 0:
        return {'items': [], 'total_count': 0}

    project_ids = [ObjectId(project_id) for project_id in user['favorite_projects']]

    query = {"_id": {"$in": project_ids}}

    projects = project_repository.get_projects(query=query, limit=limit, skip=offset, sort=sort)

    projects = paginate(projects)

    for project in projects['items']:
        if str(project['_id']) in user['favorite_projects']:
            project['last_opened_date'] = user['favorite_projects'][str(project['_id'])]['last_opened_date']

    return projects


def open_project(user_id: int, _id: str) -> dict:
    check_object_id(_id)

    user = user_service.get_user_or_fail(user_id)
    user_update = UserUpdate(**user)

    if _id not in user_update.favorite_projects:
        raise HTTPException(status_code=400, detail="Project does not exist in favorites")

    user_update.favorite_projects[_id]['last_opened_date'] = datetime.datetime.utcnow()

    user_service.update_user_by_user_id(user_id, user_update)

    return user_update.favorite_projects[_id]
