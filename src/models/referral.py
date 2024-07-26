from datetime import datetime
from typing import Optional, Annotated
from pydantic import BeforeValidator, Field, BaseModel, computed_field
from config import REFERRAL_REWARD, REFERRAL_PERCENT_REWARDS

PyObjectId = Annotated[str, BeforeValidator(str)]


class ReferralUpdated(BaseModel):
    referrer_id: Optional[int] = None
    referral_id: Optional[int] = None
    reward: Optional[int] = None

    # When changed, update config.py -> REFERRAL_PERCENT_REWARDS
    accumulated_reward: Optional[dict] = {
        'lvl1': {
            'received': REFERRAL_REWARD,
            'available': 0,
        },
        'lvl2': {
            'received': 0,
            'available': 0,
        },
        'lvl3': {
            'received': 0,
            'available': 0,
        },
    }

    updated_at: Optional[datetime] = datetime.utcnow()

    @staticmethod
    def get_excluded_fields():
        return {
            'id',
            'accumulated_reward_available',
            'accumulated_reward_received'
        }

    @computed_field
    @property
    def accumulated_reward_available(self) -> int:
        result = 0

        for level in self.accumulated_reward:
            result += self.accumulated_reward[level]['available']

        return result

    @computed_field
    @property
    def accumulated_reward_received(self) -> int:
        result = 0

        for level in self.accumulated_reward:
            result += self.accumulated_reward[level]['received']

        return result


class Referral(ReferralUpdated):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    reward: int = REFERRAL_REWARD
    created_at: Optional[datetime] = datetime.utcnow()
