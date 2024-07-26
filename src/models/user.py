from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, computed_field, Field, BeforeValidator
from config import MULTI_TAP, ENERGY_LIMIT, RECHARGING_SPEED, BOOSTERS, TAPPING_GURU
from config import USER_LEVELS

PyObjectId = Annotated[str, BeforeValidator(str)]


# User
class UserBase(BaseModel):
    @staticmethod
    def get_excluded_fields():
        return {
            'storage_id',
            'level_info',
            'energy_limit',
            'recharging_speed',
            'energy',
            'calculated_interval_boosters',
            'taping_guru_is_active',
            'tap_power',
            'full_name',
            'username_or_name',
            'total_points'
        }

    taps: Optional[int] = 0
    raw_taps: Optional[int] = 0
    points: Optional[int] = 0
    spent_points: Optional[int] = 0

    @computed_field
    @property
    def level_info(self) -> dict:
        level = 0

        for level_index, user_level in enumerate(USER_LEVELS):
            if user_level['taps'] == self.taps:
                level = level_index
                break
            elif user_level['taps'] > self.taps:
                level = level_index - 1
                break

        level_info = USER_LEVELS[level]
        return {
            'level': level,
            'title': level_info['title']
        }

    @computed_field
    @property
    def full_name(self) -> str:
        if not hasattr(self, 'first_name'):
            return ''

        full_name = self.first_name

        if hasattr(self, 'last_name') and self.last_name:
            full_name += ' ' + self.last_name

        return full_name

    @computed_field
    @property
    def username_or_name(self) -> str:
        if hasattr(self, 'username') and self.username:
            return '@' + self.username

        return self.full_name
    
    @computed_field
    @property
    def total_points(self) -> int:
        return self.points + self.spent_points


class UserBoost(BaseModel):
    current_level: int
    next_level: int
    price_step: int
    current_level_price: int
    next_level_price: int


class UserUpdate(UserBase):
    storage_id: Optional[PyObjectId] = Field(alias="_id", default=None)
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = 'en'
    is_bot: Optional[bool] = None
    is_premium: Optional[bool] = None
    updated_at: Optional[datetime] = datetime.utcnow()
    tasks: Optional[list[dict]] = []  # was supposed to be list[TaskBountyDone] type but fails while adding new tasks
    referrer: Optional[int] = None
    utm_source: Optional[str] = None
    boosters: Optional[dict] = {
        'multi_tap_boost': {"current_level": 1, "next_level": 2, "price_step": 1, "current_level_price": 0, "next_level_price": 250},
        'energy_boost': {"current_level": 1, "next_level": 2, "price_step": 1, "current_level_price": 0, "next_level_price": 250},
        'recharging_speed_boost': {"current_level": 1, "next_level": 2, "price_step": 1, "current_level_price": 0, "next_level_price": 1000},
        'auto_farming_boost': {"start_farming_date": None, "finish_farming_date": None, "max_farm_points": 0}
    }
    interval_boosters: Optional[dict] = {}
    tapping_started_date: Optional[datetime] = None
    energy_last_use: Optional[dict] = {
        'energy': 0,
        'date': None
    }
    balances: Optional[dict] = {
        'usdt': 0,
        'ton': 0
    }
    favorite_projects: Optional[dict] = {}
    last_login_date: Optional[datetime] = datetime.utcnow()
    daily_reward_progress: int = 1
    daily_reward_available: bool = False
    newsletters: Optional[list] = []
    
    @computed_field
    @property
    def energy_limit(self) -> int:
        energy_limit = ENERGY_LIMIT['start_amount']

        if 'energy_boost' in self.boosters:
            for x in range(self.boosters['energy_boost']['current_level'] - 1):
                energy_limit += ENERGY_LIMIT['energy_increment']

        return energy_limit

    @computed_field
    @property
    def recharging_speed(self) -> int:
        recharging_speed = RECHARGING_SPEED['start_amount']

        if 'recharging_speed_boost' in self.boosters:
            for x in range(self.boosters['recharging_speed_boost']['current_level'] - 1):
                recharging_speed += RECHARGING_SPEED['recharge_increment']

        return recharging_speed

    @computed_field
    @property
    def energy(self) -> int:
        if 'date' in self.energy_last_use and self.energy_last_use['date']:
            seconds_diff = (datetime.utcnow() - self.energy_last_use['date']).seconds
            energy = seconds_diff * self.recharging_speed + self.energy_last_use['energy']

            if energy > self.energy_limit:
                energy = self.energy_limit
        else:
            energy = self.energy_limit

        return energy

    @computed_field
    @property
    def calculated_interval_boosters(self) -> dict:
        boosters_cfg = BOOSTERS
        interval_boosters = self.interval_boosters

        if not interval_boosters:
            interval_boosters = {}

            for booster in boosters_cfg['interval']:
                for booster_key, booster_cfg in booster.items():
                    interval_booster_data = {
                        'amount': booster_cfg['max_amount'],
                        'recovery_date': None
                    }

                    if 'duration_seconds' in booster_cfg:
                        interval_booster_data['expiry_date'] = None

                    interval_boosters[booster_cfg['key']] = interval_booster_data

        for booster in boosters_cfg['interval']:
            for booster_key, booster_cfg in booster.items():
                interval_booster = interval_boosters[booster_cfg['key']]

                if (
                    interval_booster['amount'] == 0 and
                    interval_booster['recovery_date'] and
                    datetime.utcnow() >= interval_booster['recovery_date']
                ):
                    interval_boosters[booster_cfg['key']]['amount'] = booster_cfg['max_amount']
                    interval_boosters[booster_cfg['key']]['recovery_date'] = None

        return interval_boosters

    @computed_field
    @property
    def taping_guru_is_active(self) -> bool:
        taping_guru_is_active = False

        if ('expiry_date' in self.calculated_interval_boosters['tapping_guru'] and
                self.calculated_interval_boosters['tapping_guru']['expiry_date'] and
                datetime.utcnow() < self.calculated_interval_boosters['tapping_guru']['expiry_date']):
            taping_guru_is_active = True

        return taping_guru_is_active

    @computed_field
    @property
    def tap_power(self) -> int:
        tap_power = MULTI_TAP['start_amount']

        if 'multi_tap_boost' in self.boosters:
            for x in range(self.boosters['multi_tap_boost']['current_level'] - 1):
                tap_power += MULTI_TAP['tap_increment']

        if self.taping_guru_is_active:
            tap_power = tap_power * TAPPING_GURU['taps_multiplier']

        return tap_power


class User(UserUpdate):
    id: int
    first_name: str
    created_at: Optional[datetime] = datetime.utcnow()


class UserReferral(UserBase):
    id: int
    first_name: str
    storage_id: Optional[PyObjectId] = Field(alias="_id", default=None)
    last_name: Optional[str] = None
    reward: Optional[int] = 0
    accumulated_reward_available: Optional[float] = 0
    accumulated_reward_received: Optional[float] = 0
    accumulated_rewards: Optional[dict] = {}

    @computed_field
    @property
    def next_level_taps(self) -> int:
        return USER_LEVELS[self.level_info['level'] + 1]['taps']


class UserForLootbox(UserBase):
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
