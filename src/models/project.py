from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class ProjectUpdate(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_valid: Optional[bool] = None
    updated_at: datetime = datetime.utcnow()

    @staticmethod
    def get_excluded_fields():
        return {
            'id'
        }


class Project(ProjectUpdate):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    url: str
    created_at: datetime = datetime.utcnow()


class FavoriteProject(Project):
    last_opened_date: Optional[datetime] = None
