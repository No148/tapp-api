from typing import List

from fastapi import APIRouter, Request
from models import DemoNew, Demo
from services.demo import create_demo_record, get_all_demo_records, get_demo_or_fail, update_one_by_id

router = APIRouter()


# POST
@router.post("/", response_model=DemoNew)
async def create(demo_record: DemoNew) -> DemoNew:
    return create_demo_record(demo_record)


# PATCH
@router.patch("/{demo_id}", response_model=Demo)
async def update_one(demo_id: str, demo_record: Demo) -> Demo:
    return update_one_by_id(demo_id, demo_record)


# GET
@router.get("/", response_model=List[Demo])
async def get_all() -> List[Demo]:
    return get_all_demo_records()


@router.get("/{demo_id}", response_model=Demo)
async def get_one(demo_id: str) -> Demo:
    return get_demo_or_fail(demo_id)
