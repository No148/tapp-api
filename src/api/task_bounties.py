from fastapi import APIRouter, Depends
from models import TaskBounty
from services.task_bounty import create_task_bounty, get_task_bounties, get_task_bounty
from services.pagination import PaginatedParams, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=TaskBounty)
async def create(task: TaskBounty):
    return await create_task_bounty(task)


@router.get("/", response_model=PaginatedResponse[TaskBounty])
async def get_many(q: PaginatedParams = Depends()) -> dict:
    return await get_task_bounties(q.offset, q.sort, q.limit)


@router.get("/{task_bounty_id}", response_model=TaskBounty)
async def get_task_bounty_by_id(task_bounty_id: str) -> TaskBounty:
    result = get_task_bounty(task_bounty_id)
    return TaskBounty(**result)
