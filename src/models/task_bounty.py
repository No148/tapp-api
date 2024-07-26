from datetime import datetime
from enum import Enum
from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class TaskBountyTypes(Enum):
    SOCIAL = 'social'
    REGISTER = 'register'


class TaskBountyUpdated(BaseModel):
    storage_id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: dict
    reward: int = None
    action: Optional[str] = None
    action_checker: Optional[str] = None
    action_data: Optional[dict] = None
    type: str = 'social'
    active: bool = False,
    description: Optional[dict] = None
    required_number_of_referrals: Optional[int] = None
    league_level_index: Optional[int] = None
    daily_rewards: Optional[dict] = None
    project_id: Optional[str] = None
    lang: Optional[str] = None
    reward_per_year: Optional[int] = None
    account_age: Optional[int] = None
    updated_at: Optional[datetime] = datetime.utcnow()


class TaskBounty(TaskBountyUpdated):
    created_at: Optional[datetime] = datetime.utcnow()


class TaskBountyWithStatus(TaskBounty):
    claimed: Optional[bool] = False
    started_at: Optional[datetime] = None
    status: Optional[str] = 'todo'
    progress: Optional[float] = None
    project: Optional[dict] = None
