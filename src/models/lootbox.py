from datetime import datetime
from typing import Optional, Annotated
from pydantic import BeforeValidator, Field, BaseModel

PyObjectId = Annotated[str, BeforeValidator(str)]


class LootBoxUpdate(BaseModel):
    activated: Optional[bool] = None
    user: Optional[int] = None
    updated_at: datetime = datetime.utcnow()

    @staticmethod
    def get_excluded_fields_for_update():
        return {
            'id'
        }


class LootBox(LootBoxUpdate):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner: int
    reward: dict
    created_at: datetime = datetime.utcnow()


class LootBoxActivateBody(BaseModel):
    user: int
