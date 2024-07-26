import pytest

from fastapi.testclient import TestClient
from utils.env import ACCESS_TOKEN, MONGO_DB_NAME_TESTING, MONGO_DB_CONNECTION_STRING_TESTING
from pymongo import MongoClient
from config import USER_LEVELS, TASK_BOUNTIES
from random import randint


# Fixtures
@pytest.fixture(scope='session')
def session_monkeypatch():
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    
    yield mpatch
    
    mpatch.undo()


@pytest.fixture(scope='session', autouse=True)
def mongo_db_client(session_monkeypatch):
    mongo_client = MongoClient(MONGO_DB_CONNECTION_STRING_TESTING)
    
    session_monkeypatch.setattr('pymongo.MongoClient', lambda *args, **kwargs: mongo_client[MONGO_DB_NAME_TESTING])

    db = mongo_client[MONGO_DB_NAME_TESTING]

    yield db

    # Teardown
    for collection_name in db.list_collection_names():
        db[collection_name].drop()


@pytest.fixture(scope='session', autouse=True)
def client(mongo_db_client, seed_task_bounties):
    from main import app
    client = TestClient(app, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})
    
    yield client


# Arranging fixtures
@pytest.fixture(scope='session', autouse=True)
def seed_task_bounties(mongo_db_client) :
    mongo_db_client['tap_app_dev.task_bounties'].insert_many(TASK_BOUNTIES)

    yield


@pytest.fixture(name='task_bounty_id', scope='session', autouse=True)
def test_create_new_task_bounty(client):
    payload = {
        "title": {
            'en': "New Task Bounty",
            'ru': "Новый таск баунти"
        },
        "description": {
            'en': "This is a new task bounty",
            'ru': "Это новый таск баунти"
        },
        "reward": 1000,
        "type": "test",
        "action": "running test",
        "active": True
    }

    response = client.post('api/v1/task-bounties', json=payload)
    
    assert response.status_code == 200
    assert response.json()["title"] == payload["title"]
    
    yield response.json()['_id']


@pytest.fixture(name='user_id', scope='session')
def test_create_new_user(client):
    new_user = {
        "id": 88888888,
        "first_name": "test user"
    }

    response = client.post('api/v1/users/get-or-upsert', json=new_user)
    assert response.status_code == 200
    
    created_user = response.json()

    assert created_user["id"] == new_user["id"]
    assert created_user["first_name"] == new_user["first_name"]
    assert created_user["taps"] == 0
    assert created_user["raw_taps"] == 0
    assert created_user["level_info"]["level"] == 0
    assert created_user["level_info"]["title"] == {'en': 'wooden', 'ru': 'деревянная'}
    assert created_user["points"] == 0
    assert created_user["referrer"] is None
    assert len(created_user["tasks"]) >= 0
    assert created_user["tap_power"] == 1
    assert created_user["energy"] == 500
    assert created_user["energy_limit"] == 500
    assert created_user["recharging_speed"] == 1

    assert "last_name" in created_user
    assert "username" in created_user
    assert "language_code" in created_user
    assert "is_bot" in created_user
    assert "is_premium" in created_user
    assert "referrer" in created_user
    assert "boosters" in created_user and "multi_tap_boost" in created_user['boosters']
    assert "boosters" in created_user and "energy_boost" in created_user['boosters']
    assert "boosters" in created_user and "recharging_speed_boost" in created_user['boosters']
    assert "interval_boosters" in created_user

    assert created_user['boosters']['multi_tap_boost']['current_level'] == 1
    assert created_user['boosters']['multi_tap_boost']['next_level'] == 2
    assert created_user['boosters']['multi_tap_boost']['price_step'] == 1
    assert created_user['boosters']['multi_tap_boost']['current_level_price'] == 0
    assert created_user['boosters']['multi_tap_boost']['next_level_price'] == 250

    assert created_user['boosters']['energy_boost']['current_level'] == 1
    assert created_user['boosters']['energy_boost']['next_level'] == 2
    assert created_user['boosters']['energy_boost']['price_step'] == 1
    assert created_user['boosters']['energy_boost']['current_level_price'] == 0
    assert created_user['boosters']['energy_boost']['next_level_price'] == 250

    assert created_user['boosters']['recharging_speed_boost']['current_level'] == 1
    assert created_user['boosters']['recharging_speed_boost']['next_level'] == 2
    assert created_user['boosters']['recharging_speed_boost']['price_step'] == 1
    assert created_user['boosters']['recharging_speed_boost']['current_level_price'] == 0
    assert created_user['boosters']['recharging_speed_boost']['next_level_price'] == 1000

    assert created_user['energy_last_use']['energy'] == 0
    assert created_user['energy_last_use']['date'] is None

    assert "created_at" in created_user
    assert "updated_at" in created_user
    
    # Create one referral with each levels
    for lvl in USER_LEVELS:
        user_data = {
            "first_name": lvl['title']['en'],
            "referrer": created_user['id'],
            "id": randint(1000000, 9999999),
            "raw_taps": lvl['taps'],
            'taps': lvl['taps'] + 100
        }

        response = client.post('api/v1/users/get-or-upsert', json=user_data)
        assert response.status_code == 200

    # Create boosted test user
    boosted_user_data = {
        "first_name": "boosted_test_user",
        "id": 5858585858,
        "raw_taps": 100000,
        "taps": 200000,
        "interval_boosters": {
            "tapping_guru": {
                "amount": 1,
                "recovery_date": None,
                "expiry_date": None
            },
            "energy_refresh": {
                "amount": 2,
                "recovery_date": None
            }
        },
        "boosters": {
            "multi_tap_boost": {
                "current_level": 1,
                "next_level": 2,
                "price_step": 1,
                "current_level_price": 0,
                "next_level_price": 250
            },
            "energy_boost": {
                "current_level": 1,
                "next_level": 2,
                "price_step": 1,
                "current_level_price": 0,
                "next_level_price": 250
            },
            "recharging_speed_boost": {
                "current_level": 1,
                "next_level": 2,
                "price_step": 1,
                "current_level_price": 0,
                "next_level_price": 1000
            }
        }
    }

    response = client.post('api/v1/users/get-or-upsert', json=boosted_user_data)

    assert response.status_code == 200

    yield created_user['id']


@pytest.fixture(name='user_before')
def get_user_before(client, user_id):
    response = client.get(f'api/v1/users/{user_id}')

    assert response.status_code == 200

    return response.json()

