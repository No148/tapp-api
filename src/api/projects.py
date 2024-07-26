from fastapi import APIRouter, HTTPException, Depends
from models import Project, ProjectUpdate
from services.pagination import PaginatedParams, PaginatedResponse
from services.project import (
    create_project,
    get_projects,
    update_metadata,
    update_fields,
    validate
)

router = APIRouter()


@router.post("/", response_model=Project)
async def create(project: Project) -> Project:
    result = await create_project(project)

    if 'error_msg' in result:
        raise HTTPException(status_code=result['error_code'], detail=result['error_msg'])

    return result


@router.get("/", response_model=PaginatedResponse[Project])
async def get_many(
        q: PaginatedParams = Depends(),
        _id: str = None,
        is_valid: bool = None,
        title: str = None) -> dict:

    return await get_projects(q.offset, q.sort, q.limit, _id, is_valid, title)


@router.get("/update-metadata", response_model=dict)
async def do_update_metadata() -> dict:
    return update_metadata()


@router.post("/{project_id}/update", response_model=Project)
async def update_fields_route(project_id: str, project_update: ProjectUpdate) -> Project:
    return update_fields(project_id, project_update)


@router.post("/{project_id}/validate", response_model=Project)
async def validate_route(project_id: str, project_update: ProjectUpdate) -> Project:
    return validate(project_id, project_update)
