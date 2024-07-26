from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, computed_field, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class DemoBase(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = None

    @staticmethod
    def get_excluded_fields():
        return {
            'id',
            'demo_computed'
        }

    @computed_field
    @property
    def demo_computed(self) -> int:
        return 1 + 1


class Demo(DemoBase):
    title: Optional[str] = None
    description: Optional[str] = None
    balances: Optional[dict] = {
        'USDT': 0,
        'TON': 0
    }
    mandatory_int: Optional[int] = None
    updated_at: datetime = datetime.utcnow()


class DemoNew(Demo):
    title: str
    mandatory_int: int
    created_at: datetime = datetime.utcnow()


class DemoUpdate(Demo):
    title: str
    mandatory_int: int
    updated_at: datetime = datetime.utcnow()
