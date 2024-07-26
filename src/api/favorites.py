from fastapi import APIRouter, Depends
from services.favorites import add_project, delete_project, get_projects, open_project
from services.pagination import PaginatedParams, PaginatedResponse
from models import Project, FavoriteProject

router = APIRouter()


@router.put("/projects/{user_id}", response_model=list)
async def add_api(user_id: int, body: dict) -> list:
    return add_project(user_id, body)


@router.delete("/projects/{user_id}/{_id}", response_model=list)
async def delete_api(user_id: int, _id: str) -> list:
    return delete_project(user_id, _id)


@router.post("/projects/{user_id}/{_id}/open", response_model=dict)
async def open_api(user_id: int, _id: str) -> dict:
    return open_project(user_id, _id)


@router.get("/projects/{user_id}", response_model=PaginatedResponse[FavoriteProject])
async def get_favorites_api(user_id: int, q: PaginatedParams = Depends()) -> dict:
    return get_projects(user_id, q.sort, q.limit, q.offset)
