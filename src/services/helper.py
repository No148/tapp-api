from bson import ObjectId
from fastapi import HTTPException


def check_object_id(value: str) -> str:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail='Invalid ObjectId')
    return value
