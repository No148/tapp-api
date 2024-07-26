import urllib.parse

from bson import ObjectId
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from utils.env import TAPPING_GURU_INTERVAL_HOURS, ENERGY_REFRESH_INTERVAL_HOURS, WEBAPP_URL, BOT_USERNAME

REFERRAL_REWARD = 2500
TASK_CONFIRMATION_MINUTES = 30

# daily boosters
# refresh every 6 hours
TAPPING_GURU = {
    'key': 'tapping_guru',
    'title': {
        'en': 'Taping guru',
        'ru': 'Тапинг гуру'
    },
    'description': {
        'en': 'Each tap multiplies by 5 for 30 seconds',
        'ru': 'Каждое нажатие увеличивает тап в 5 раз в течении 30 секунд'
    },
    'max_amount': 3,
    'interval_hours': TAPPING_GURU_INTERVAL_HOURS,
    'duration_seconds': 30,
    'taps_multiplier': 5
}
# refresh every 12 hours
ENERGY_REFRESH = {
    'key': 'energy_refresh',
    'title': {
        'en': 'Full tank',
        'ru': 'Полный бак'
    },
    'description': {
        'en': 'Instantly restores 100% of energy',
        'ru': 'Мгновенно восстановит энергию на 100%'
    },
    'max_amount': 3,
    'interval_hours': ENERGY_REFRESH_INTERVAL_HOURS
}

# 200 500 1000 2000 4000 8000 16000 25000 50000 100000
MULTI_TAP = {
    'start_price': 250,
    'start_amount': 1,
    'price_factor': 2,
    'tap_increment': 1,
    'user_model_field': 'multi_tap_level',
    'title': {
        'en': 'Multitap',
        'ru': 'Мультитап'
    },
    'description': {
        'en': '+1 to tap power for each level',
        'ru': '+1 увеличение мощности тапа за каждый уровень'
    }
}

# 200 500 1000 2000 4000 8000 16000
ENERGY_LIMIT = {
    'start_price': 250,
    'start_amount': 500,
    'price_factor': 2,
    'energy_increment': 500,
    'user_model_field': 'energy_level',
    'title': {
        'en': 'Energy limit',
        'ru': 'Лимит энергии'
    },
    'description': {
        'en': '+500 to your max energy amount for each level',
        'ru': '+500 к максимальному количеству энергии за каждый уровень '
    }
}

# 2000 10000 100000 250000
RECHARGING_SPEED = {
    'start_price': 1000,
    'start_amount': 1,
    'price_factor': 10,
    'recharge_increment': 1,
    'user_model_field': 'recharge_level',
    'title': {
        'en': 'Recharging speed',
        'ru': 'Скорость восстановления'
    },
    'description': {
        'en': '+1 to amount of energy restored for 1 second for each level',
        'ru': '+1 к количеству восстанавливаемой энергии за 1 секунду за каждый уровень'
    }
}

BOOST_PRICE_CHANGER = {
    "multi_tap_boost": [
        {"factor": 2, "step": 1}, {"factor": 2, "step": 2}, {"factor": 2, "step": 3},
        {"percent": 60, "step": 4}, {"factor": 2, "step": 5}, {"factor": 2, "step": 6}, {"factor": 2, "step": 7}
    ],
    "energy_boost": [
        {"factor": 2, "step": 1}, {"sum": 8000, "step": 2}, {"factor": 10, "step": 3},
        {"sum": 150000, "step": 4}, {"factor": 2, "step": 5}, {"sum": 100000, "step": 6}, {"factor": 2, "step": 7}
    ],
    "recharging_speed_boost": [
        {"factor": 2, "step": 1}, {"factor": 2, "step": 2}, {"factor": 2, "step": 3},
        {"percent": 60, "step": 4}, {"factor": 2, "step": 5}, {"factor": 2, "step": 6}, {"factor": 2, "step": 7}
    ],
}

BOOSTERS = {
    'interval': [
        {'tapping_guru': TAPPING_GURU},
        {'energy_refresh': ENERGY_REFRESH},
    ],
    'purchasable': [
        {'multi_tap_boost': MULTI_TAP},
        {'energy_boost': ENERGY_LIMIT},
        {'recharging_speed_boost': RECHARGING_SPEED}
    ]
}

USER_LEVELS = [
    {'title': {'en': 'wooden', 'ru': 'деревянная'}, 'taps': 0},
    {'title': {'en': 'bronze', 'ru': 'бронзовая'}, 'taps': 1},
    {'title': {'en': 'silver', 'ru': 'серебряная'}, 'taps': 5000},
    {'title': {'en': 'gold', 'ru': 'золотая'}, 'taps': 50000},
    {'title': {'en': 'platinum', 'ru': 'платиновая'}, 'taps': 250000},
    {'title': {'en': 'diamond', 'ru': 'алмазная'}, 'taps': 500000},
    {'title': {'en': 'master', 'ru': 'мастер'}, 'taps': 1000000},
    {'title': {'en': 'grandmaster', 'ru': 'грендмастер'}, 'taps': 2500000},
    {'title': {'en': 'elite', 'ru': 'элитная'}, 'taps': 5000000},
    {'title': {'en': 'legendary', 'ru': 'легендарная'}, 'taps': 10000000},
    {'title': {'en': 'mythic', 'ru': 'мифическая'}, 'taps': 500000000},
]

# When changed, update ReferralUpdated -> accumulated_reward
REFERRAL_PERCENT_REWARDS = {
    'lvl1': 10,
    'lvl2': 5,
    'lvl3': 2,
}

MINIMUM_CLAIM_ACCUMULATED_REWARD = 100

TASK_BOUNTIES = [
    {
        '_id': ObjectId('6658219ff47a17241f9e6af1'),
        'title': {
            'en': 'Daily reward',
            'ru': 'Ежедневная награда'
        },
        'type': 'daily_reward',
        'description': {
            'en': 'Daily reward',
            'ru': 'Ежедневная награда'
        },
        'active': True
    },
    {
        '_id': ObjectId('6658219ff47a17441f9e6af9'),
        'title': {
            'en': 'Join our TG channel',
            'ru': 'Подпишитесь на наш тг канал'
        },
        'reward': 5000,
        # 'action_data': {
        #     'ru': {
        #         'link': 'https://t.me/+Ukgrl9JndkiyjYop',
        #         'id': '-1001380461463'
        #     }
        # },
        'action_data': {
            'ru': {
                'link': 'https://t.me/SecretTonProjectRU',
                'id': '-1002187735854'
            },
            'en': {
                'link': 'https://t.me/SecretTonProject',
                'id': '-1001704501466'
            }
        },
        'action_checker': 'telegram_join',
        'type': 'social',
        'description': {
            'en': 'Description join to ur mega TG channel now @channel',
            'ru': 'Подпишитесь на наш тг канал'
        },
        'active': True
    },
    {
        '_id': ObjectId('6658219ff47a17431f9e6af1'),
        'title': {
            'en': 'Boost our TG channel',
            'ru': 'Забусти наш тг канал'
        },
        'reward': 100000,
        # 'action': 'https://t.me/+Ukgrl9JndkiyjYop',
        # 'action_data': {
        #     'channel_id': '-1001380461463'
        # },
        'action': 'https://t.me/SecretTonProject?boost',
        'action_data': {
            'channel_id': '-1001704501466'
        },
        'action_checker': 'telegram_boost',
        'type': 'social',
        'description': {
            'en': 'Boost TG channel now',
            'ru': 'Забусти наш тг канал'
        },
        'active': True
    },
    {
        '_id': ObjectId('666bf1515095999381b1867b'),
        'description': {
            'en': "Invite 3 friends",
            'ru': 'Пригласи 3 друзей'
        },
        'reward': 100000,
        'title': {
            'en': "Invite 3 friends",
            'ru': 'Пригласи 3 друзей'
        },
        'type': "ref",
        'required_number_of_referrals': 3,
        'active': True
    },
    {
        '_id': ObjectId('666bf2005095999381b1867c'),
        'description': {
            'en': "Invite 10 friends",
            'ru': 'Пригласи 10 друзей'
        },
        'reward': 400000,
        'title': {
            'en': "Invite 10 friends",
            'ru': 'Пригласи 10 друзей'
        },
        'type': "ref",
        'required_number_of_referrals': 10,
        'active': True
    },
    {
        '_id': ObjectId('666bf2105095999381b1867d'),
        'description': {
            'en': "Invite 25 friends",
            'ru': 'Пригласи 25 друзей'
        },
        'reward': 500000,
        'title': {
            'en': "Invite 25 friends",
            'ru': 'Пригласи 25 друзей'
        },
        'type': "ref",
        'required_number_of_referrals': 25,
        'active': True
    },
    {
        '_id': ObjectId('666bf2335095999381b1867e'),
        'description': {
            'en': "Invite 50 friends",
            'ru': 'Пригласи 50 друзей'
        },
        'reward': 600000,
        'title': {
            'en': "Invite 50 friends",
            'ru': 'Пригласи 50 друзей'
        },
        'type': "ref",
        'required_number_of_referrals': 50,
        'active': True
    },
    {
        '_id': ObjectId('666bf24c5095999381b1867f'),
        'description': {
            'en': "Silver",
            'ru': 'Серебро'
        },
        'reward': 5000,
        'title': {
            'en': "Silver",
            'ru': 'Серебро'
        },
        'type': "league",
        'league_level_index': 2,
        'active': True
    },
    {
        '_id': ObjectId('666bf2ce5095999381b18680'),
        'description': {
            'en': "Gold",
            'ru': 'Золото'
        },
        'reward': 10000,
        'title': {
            'en': "Gold",
            'ru': 'Золото'
        },
        'type': "league",
        'league_level_index': 3,
        'active': True
    },
    {
        '_id': ObjectId('666bf2dc5095999381b18681'),
        'description': {
            'en': "Platinum",
            'ru': 'Платина'
        },
        'reward': 30000,
        'title': {
            'en': "Platinum",
            'ru': 'Платина'
        },
        'type': "league",
        'league_level_index': 4,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b18682'),
        'description': {
            'en': "Diamond",
            'ru': 'Алмаз'
        },
        'reward': 50000,
        'title': {
            'en': "Diamond",
            'ru': 'Алмаз'
        },
        'type': "league",
        'league_level_index': 5,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b18683'),
        'description': {
            'en': "Master",
            'ru': 'Мастер'
        },
        'reward': 100000,
        'title': {
            'en': "Master",
            'ru': 'Мастер'
        },
        'type': "league",
        'league_level_index': 6,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b18684'),
        'description': {
            'en': "Grandmaster",
            'ru': 'Грендмастер'
        },
        'reward': 250000,
        'title': {
            'en': "Grandmaster",
            'ru': 'Грендмастер'
        },
        'type': "league",
        'league_level_index': 7,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b18685'),
        'description': {
            'en': "Elite",
            'ru': 'Элита'
        },
        'reward': 500000,
        'title': {
            'en': "Elite",
            'ru': 'Элита'
        },
        'type': "league",
        'league_level_index': 8,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b18686'),
        'description': {
            'en': "Legendary",
            'ru': 'Легендарный'
        },
        'reward': 1000000,
        'title': {
            'en': "Legendary",
            'ru': 'Легендарный'
        },
        'type': "league",
        'league_level_index': 9,
        'active': True
    },
    {
        '_id': ObjectId('666bf2fc5095999381b19687'),
        'description': {
            'en': "Mythic",
            'ru': 'Мифический'
        },
        'reward': 5000000,
        'title': {
            'en': "Mythic",
            'ru': 'Мифический'
        },
        'type': "league",
        'league_level_index': 10,
        'active': True
    },
    {
        '_id': ObjectId('6690c2b1b6f7b31f0c63e120'),
        'description': {
            'en': "Add project",
            'ru': 'Добавить проект'
        },
        'reward': 10000,
        'title': {
            'en': "Add project",
            'ru': 'Добавить проект'
        },
        'type': "add_project",
        'active': True
    },
    {
        "_id": ObjectId("669625df6872fb875e0d5b67"),
        "description": {
            "en": "Connect TON wallet",
            "ru": "Подключи TON кошелёк"
        },
        "reward": 10000,
        "title": {
            "en": "Connect TON wallet",
            "ru": "Подключи TON кошелёк"
        },
        "type": "connect_wallet",
        "active": False
    },
    {
        "_id": ObjectId("669626db6872fb875e0d5b68"),
        "description": {
            "en": "Connect Twitter(X) account",
            "ru": "Подключи Twitter(X) аккаунт"
        },
        "reward": 5000,
        "title": {
            "en": "Connect Twitter(X) account",
            "ru": "Подключи Twitter(X) аккаунт"
        },
        "type": "social",
        "active": False
    },
    {
        "_id": ObjectId("66a03a8bf14e5938fd66d8e2"),
        "description": {
            "en": "Age of account",
            "ru": "Возраст аккаунт"
        },
        "title": {
            "en": "Age of account",
            "ru": "Возраст аккаунт"
        },
        "type": "age_of_account",
        "active": True
    }
]

DAILY_TASK_REWARDS = {
    1: 500,
    2: 1000,
    3: 5000,
    4: 15000,
    5: 25000,
    6: 50000,
    7: 75000,
    8: 100000,
    9: 200000
}

EXCLUDE_PROJECTS = {
    'secretpadbot'
}


def bot_menu_buttons(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Play in 1 click 💸', web_app=WebAppInfo(url=WEBAPP_URL))
        ],
        [
            InlineKeyboardButton('🤑 Invite Friends 🤑!', url=f"https://t.me/share/url?url={urllib.parse.quote(f'https://t.me/{BOT_USERNAME}/app?startapp=r{chat_id}', safe='')}&text={urllib.parse.quote(f'🎁 +{REFERRAL_REWARD} Coins as a first-time gift')}"),
        ],
        [
            InlineKeyboardButton('Обмен Трафиком? RU', url='https://t.me/TapalkaFounders'),
        ],
        [
            InlineKeyboardButton('Ты КОЛ/Инфлюенсер? RU', url='https://t.me/SecretTonKOLsR'),
        ],
        [
            InlineKeyboardButton('Вопросы? Ответим! RU', url='https://t.me/SecretTonSupportRU'),
        ],
        [
            InlineKeyboardButton('Need Support? EN', url='https://t.me/SecretTonSupport'),
        ],
        [
            InlineKeyboardButton('Partnerships? Traffic Exchange? EN', url='https://t.me/TONappFounders'),
        ]
    ])


# Farming time in hours
FARMING_TIME = 6

# Farming speed time
FARMING_SPEED_TIME = 3600

# Farming: referrals - points
FARMING_REFERRALS_POINTS = {
    1: 2000,
    2: 5000,
    3: 7500,
    4: 10000,
    5: 15000,
    6: 20000
}

AGE_OF_ACCOUNT = {
    1900000000: 2024,
    1800000000: 2023,
    1700000000: 2022,
    1500000000: 2021,
    1100000000: 2020,
    800000000: 2019,
    500000000: 2018,
    400000000: 2017,
    200000000: 2016,
    100000000: 2015,
    0: 2014,
}

ACCOUNT_AGE_PER_YEAR_REWARD = 5000
