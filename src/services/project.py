import requests
import utils.helper as helper_utils
import telegram
import services.user_referral_url as user_referral_url_service

from fastapi import HTTPException
from bs4 import BeautifulSoup
from repository import ProjectRepository
from bson import ObjectId
from models import Project, ProjectUpdate
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.env import PROJECT_MODERATION_CHAT_ID, BOT_TOKEN
from services.pagination import paginate
from config import EXCLUDE_PROJECTS

project_repository = ProjectRepository()


async def create_project(project: Project) -> Project | dict:
    message_err_invalid_project_url = 'Invalid provided projects url link. Examples: t.me/MyApp_Bot; https://t.me/MyAppBot'
    project.url = project.url.lower()

    min_characters_in_url = 11
    is_bot_ref_url = project.url.endswith("bot")

    if not project.url or len(project.url) < min_characters_in_url or 't.me/' not in project.url or not is_bot_ref_url:
        raise HTTPException(status_code=400, detail=message_err_invalid_project_url)

    if any(exclude_project in project.url for exclude_project in EXCLUDE_PROJECTS):
        raise HTTPException(status_code=400, detail='Sorry, current bot can not be added')

    if not any(vsu in project.url for vsu in ['http://', 'https://']):
        if project.url[:5] == 't.me/':
            project.url = 'https://' + project.url
        else:
            raise HTTPException(status_code=400, detail=message_err_invalid_project_url)

    exist_project = project_repository.get_one({"url": {"$regex": project.url, "$options": "i"}})

    if exist_project:
        return Project(**exist_project)

    project_metadata = get_metadata_by_user_referral_url(project.url)

    if project_metadata:
        project.title = project_metadata['title']
        project.description = project_metadata['description']
        project.url = project.url
    else:
        raise HTTPException(status_code=400, detail=f'Can not get metadata for project by provided url: {project.url}')

    project_dict = project.model_dump(exclude=project.get_excluded_fields())

    created_project = Project(**project_repository.create_one(project_dict))

    if project_metadata['image_url']:
        image_url = helper_utils.download_image_by_url(
            url=project_metadata['image_url'],
            filename=created_project.id,
            path='project_imgs'
        )

        if image_url:
            project_repository.update_one(
                query={"_id": ObjectId(created_project.id)},
                update={"$set": {"image_url": image_url}}
            )

            created_project.image_url = image_url

    await telegram.Bot(token=BOT_TOKEN).send_message(
        chat_id=PROJECT_MODERATION_CHAT_ID,
        text=f'Project URL: {project.url}',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text='✅ Approve',
                    callback_data=f"approve_project_{created_project.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Reject',
                    callback_data=f"reject_project_{created_project.id}"
                )
            ],
        ])
    )

    return created_project


async def get_projects(skip: int = 0, sort: str = None, limit: int = 50, _id: str = None, is_valid: bool = None, title: str = None) -> dict:
    query = {}

    if _id:
        query["_id"] = ObjectId(_id)

    if title:
        query["title"] = {"$regex": title, "$options": "i"}

    if is_valid is not None:
        query["is_valid"] = is_valid

    result = project_repository.get_projects(query=query, limit=limit, skip=skip, sort=sort)

    return paginate(result)


def get_metadata_by_user_referral_url(url: str = None) -> dict:
    try:
        if not url:
            return {}

        request_data = requests.get(url)

        html_doc = request_data.content
        soup = BeautifulSoup(html_doc, 'html.parser')

        image = soup.find('meta', {'property': 'og:image'})
        title = soup.find('meta', {'property': 'og:title'})
        description = soup.find('meta', {'property': 'og:description'})
        robots = soup.find('meta', {'name': 'robots'})

        if robots:
            return {}

        if image and (image.get('content') == 'https://telegram.org/img/t_logo.png' or 't_logo' in image.get('content')):
            image = None

        return {
            'title': title.get('content') if title else None,
            'description': description.get('content') if description else None,
            'image_url': image.get('content') if image else None
        }
    except Exception as err:
        print(f"Got error while trying get metadata from url: {url}. \r\n Error:\r\n {err}")

        return {}


def update_metadata() -> dict:
    projects = list(project_repository.get_many())

    for project in projects:
        try:
            if not project['url']:
                print(f'While updating project metadata. No url for project: {project["_id"]}. Skip it')
                continue

            if not any(match_str in project['url'] for match_str in ['http://', 'https://']):
                project['url'] = 'https://' + project['url']

            metadata = get_metadata_by_user_referral_url(project['url'])

            if metadata:
                image_url = None

                data = {
                    "title": metadata["title"],
                    "description": metadata["description"]
                    }

                if metadata["image_url"]:
                    image_url = helper_utils.download_image_by_url(
                        url=metadata['image_url'],
                        filename=str(project["_id"]),
                        path='project_imgs'
                    )

                if image_url:
                    data["image_url"] = image_url

                project_repository.update_one(query={"_id": project["_id"]}, update={"$set": data})
        except Exception as err:
            print(f"Error while updating metadata for project: {project['_id']}. Skip. \r\n Error:\r\n {err}")

    return {"finished": True, "message": "Successfully finished updating projects metadata"}


def get_project(project_id: str) -> Project:
    project = project_repository.get_one(query={'_id': ObjectId(project_id)})

    return Project(**project) if project else None


def check_on_exist_project(project_id: str) -> bool:
    return bool(project_repository.get_one(query={'_id': ObjectId(project_id)}))


def check_on_exist_project_by_url_regex(url: str) -> bool:
    return bool(project_repository.get_one(query={"url": {"$regex": url, "$options": "i"}}))


def get_project_or_fail(project_id: str) -> Project:
    project = None

    try:
        project = get_project(project_id)
    except Exception as err:
        print(f'Error: \r\n {err}')

    if not project:
        raise HTTPException(status_code=404, detail='Project not found')

    return project


def update_project_by_id(project_id: str, model_update: ProjectUpdate) -> dict:
    model_update_dict = model_update.model_dump(exclude_unset=True)

    project_repository.update_one(
        query={"_id": ObjectId(project_id)},
        update={"$set": model_update_dict}
    )

    return model_update_dict


def update_fields(project_id: str, project_update: ProjectUpdate) -> Project:
    project = get_project_or_fail(project_id)
    project_dict = update_project_by_id(project_id, project_update)
    project_updated = project.model_copy(update=project_dict)

    return project_updated


def validate(project_id: str, project_update: ProjectUpdate) -> Project:
    project = project_repository.get_one({'_id': ObjectId(project_id)})

    if not project:
        raise HTTPException(status_code=404, detail=f'Project: {project_id} not found')

    project = Project(**project)

    project_repository.update_one(
        query={"_id": ObjectId(project_id)},
        update={"$set": {"is_valid": project_update.is_valid}}
    )
    user_referral_url_service.validate_by_project_id(project_id, project_update.is_valid)

    project_updated = project.model_copy(update=project_update.model_dump(exclude_unset=True))

    return project_updated
