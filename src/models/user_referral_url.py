from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserReferralUrl(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    url: str
    user_tg_id: int
    referrer_count: Optional[int] = 0
    is_valid: Optional[bool] = None
    project_id: Optional[PyObjectId] = None
    project: Optional[dict] = {}
    created_at: Optional[datetime] = datetime.utcnow()
    updated_at: Optional[datetime] = datetime.utcnow()

    @staticmethod
    def get_excluded_fields():
        return {
            'id',
            'project'
        }
