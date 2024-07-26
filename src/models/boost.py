from typing import Optional, Annotated
from pydantic import BaseModel, BeforeValidator
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]


class Boost(BaseModel):
    user_id: int
    boost: str
    current_level: Optional[int] = None
    next_level: Optional[int] = None
    next_level_price: Optional[int] = None
    created_at: Optional[datetime] = datetime.utcnow()
