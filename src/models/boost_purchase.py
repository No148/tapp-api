from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class BoostPurchase(BaseModel):
    user_id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_tg_id: int
    boost: str
    level: int
    price: int
    created_at: Optional[datetime] = datetime.utcnow()
