from typing import Generic, TypeVar, Annotated
from pydantic import Field, BaseModel
from fastapi import Query
from typing import List

M = TypeVar('M')


class PaginatedParams:
    def __init__(
            self,
            page: int = Query(1, ge=1),
            limit: int = Query(100, ge=0),
            sort: Annotated[str, Query(min_length=2)] = '-created_at'
    ):
        self.limit = limit
        self.offset = (page - 1) * limit
        self.sort = {sort[1:]: -1} if sort[0] == '-' else {sort[0:]: 1}


class PaginatedResponse(BaseModel, Generic[M]):
    total_count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')


def paginate(result: dict) -> dict:
    result = list(result)

    return {
        'total_count': result[0]['pagination'][0]['total'] if result[0] and result[0]['pagination'] else 0,
        'items': result[0]['data'] if result and result[0] and result[0]['data'] else []
    }
