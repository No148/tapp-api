from datetime import datetime
from typing import Optional, Annotated
from pydantic import BeforeValidator, Field, BaseModel

PyObjectId = Annotated[str, BeforeValidator(str)]


class NewsletterUpdate(BaseModel):
    text: Optional[str] = None
    photo_id: Optional[str] = None
    status: Optional[str] = None # new, in_progress / success / error
    updated_at: datetime = datetime.utcnow()

    @staticmethod
    def get_excluded_fields():
        return {
            'id'
        }


class Newsletter(NewsletterUpdate):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = datetime.utcnow()
