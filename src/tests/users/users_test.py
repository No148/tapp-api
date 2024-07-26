import pytest

from config import BOOSTERS
from pprint import pprint

def get_or_upsert_user(client, user_id):
    response = client.get(
        f'api/v1/user/get-or-upsert',
        json={
            'id': user_id
        }
    )

    assert response.status_code == 200

    return response.json()


# User
def test_update_user(client, user_id):
    new_data = {
        "username": "test",
        "last_name": "user",
    }

    response = client.patch(f'api/v1/users/{user_id}', json=new_data)

    # Assert
    assert response.status_code == 200
    
    updated_user = response.json()
    
    assert updated_user['username'] == new_data['username']
    assert updated_user['last_name'] == new_data['last_name']


def test_get_user(client, user_id):
    response = client.get(f'api/v1/users/{user_id}')

    assert response.status_code == 200
    
    user = response.json()
   
    assert 'id' in user
    assert 'first_name' in user


def test_add_taps(client, user_id, user_before):
    response = client.post(f'api/v1/users/{user_id}/add-taps', json={"taps": 100})
    
    assert response.status_code == 200

    user_after = response.json()

    assert user_before["raw_taps"] + 100 == user_after["raw_taps"]
    

def test_add_taps_negative(client, user_id):
    response = client.post(f'api/v1/users/{user_id}/add-taps', json={"taps": -100})
    
    assert response.status_code == 400


def test_add_taps_more_than_energy(client, user_id):
    response = client.post(f'api/v1/users/{user_id}/add-taps', json={"taps": 100000})
    
    assert response.status_code == 400

    
def test_add_user_points(client, user_id, user_before):
    response = client.post(f'api/v1/users/{user_id}/add-points', json={"points": 50000})
    
    assert response.status_code == 200

    user_after = response.json()
    
    assert user_before['points'] + 50000 == user_after['points']


def test_add_task_bounty(client, user_id, task_bounty_id):
    response = client.post(f'api/v1/users/{user_id}/add-task-bounty/{task_bounty_id}', json={})
    assert response.status_code == 200


def test_get_user_by_id(client, user_id):
    response = client.get(f'api/v1/users/{user_id}', )
    
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_user_referrals(client, user_id):
    response = client.get(f'api/v1/users/{user_id}/referrals')
        
    assert response.status_code == 200
    assert len(response.json()['referrals']) >= 0

    referrals = response.json()['referrals']
    must_exist_fields = ['_id', 'taps', 'raw_taps', 'points', 'first_name', 'last_name', 'reward', 'level_info', 'next_level_taps', 'accumulated_reward_available', 'accumulated_reward_received']

    for referral in referrals:
        for field in must_exist_fields:
            assert field in referral

    assert 'percent_rewards' in response.json()

    
def test_get_user_task_bounties_ref(client, user_id):
    # Get task bounties
    response = client.get(f'api/v1/users/{user_id}/task-bounties')  
    
    user_task_bounties = response.json()['items']

    assert response.status_code == 200  
    assert len(user_task_bounties) >= 0

    # Assert task bounty 'Invite 3 friends' and 'Invite 10 friends' should be claimable 
    task_bounty = [task for task in user_task_bounties if task['description']['en'] in ['Invite 3 friends', 'Invite 10 friends']]
    assert task_bounty[0]['progress'] == 100.0
    assert task_bounty[0]['status'] == 'claimable'


def test_get_user_task_bounties_leagues(client, mongo_db_client):
    gold_league_user = mongo_db_client['tap_app_dev.users'].find_one({"first_name": "gold"})
    
    assert gold_league_user is not None

    # Get task bounties
    response = client.get(f'api/v1/users/{gold_league_user["id"]}/task-bounties')  

    gold_league_user_task_bounties = response.json()['items']

    for task_bounty in gold_league_user_task_bounties:
        if task_bounty['type'] == 'league' and task_bounty['title']['en'] in ['Silver', 'Gold']:
                assert task_bounty['progress'] == 100.0
                assert task_bounty['status'] == 'claimable'

        if task_bounty['type'] == 'league' and task_bounty['title']['en'] == 'Platinum':
                assert task_bounty['progress'] < 100
                assert task_bounty['status'] == 'todo'

    mythic_league_user = mongo_db_client['tap_app_dev.users'].find_one({"first_name": "mythic"})
    
    assert mythic_league_user is not None

    # Get task bounties
    response = client.get(f'api/v1/users/{mythic_league_user["id"]}/task-bounties')  

    mythic_league_user_task_bounties = response.json()['items']

    for task_bounty in mythic_league_user_task_bounties:
        if task_bounty['type'] == 'league':
                assert task_bounty['progress'] == 100.0
                assert task_bounty['status'] == 'claimable'


def test_get_user_boosters(client, user_before):
    response = client.get(f'api/v1/users/{user_before["id"]}/boosters')
    
    assert response.status_code == 200
    assert len(response.json()) >= 0

    user_points = user_before["points"]
    user_boosters_response = response.json()
    user_boosters = user_before["boosters"]

    assert user_points == user_boosters_response["available_points"]
    assert "interval" in user_boosters_response
    assert "purchasable" in user_boosters_response

    interval_boosters = user_boosters_response["interval"]
    purchasable_boosters = user_boosters_response["purchasable"]

    for i_booster in interval_boosters:
        booster_cfg = [booster_cfg[i_booster["key"]] for booster_cfg in BOOSTERS["interval"] if i_booster["key"] in booster_cfg]
        booster_cfg = booster_cfg[0]

        if 'duration_seconds' in i_booster:
            assert i_booster["duration_seconds"] == booster_cfg["duration_seconds"]

        assert i_booster["key"] == booster_cfg["key"]
        assert i_booster["amount"] == booster_cfg["max_amount"]
        assert i_booster["recovery_date"] is None
         
    for p_booster in purchasable_boosters:        
        p_user_booster = user_boosters[p_booster["key"]]

        assert p_booster["level"] == p_user_booster["current_level"]
        assert p_booster["next_level"] == p_user_booster["next_level"]
        assert p_booster["next_price"] == p_user_booster["next_level_price"]


def test_get_user_with_boosters(client):
    user_boosters_response = client.get(f'api/v1/users/5858585858/boosters')
    
    assert user_boosters_response.status_code == 200

    user_response = client.get(f'api/v1/users/5858585858')
    
    assert user_response.status_code == 200

    user_response = user_response.json()
    user_boosters = user_response["boosters"]
    user_interval_boosters = user_response["interval_boosters"]
    user_points = user_response["points"]
    user_boosters_response = user_boosters_response.json()

    assert user_points == user_boosters_response["available_points"]
    assert "interval" in user_boosters_response
    assert "purchasable" in user_boosters_response

    interval_boosters = user_boosters_response["interval"]
    purchasable_boosters = user_boosters_response["purchasable"]

    for i_booster in interval_boosters:
        i_user_booster = user_interval_boosters[i_booster["key"]]

        assert i_booster["amount"] == i_user_booster["amount"]
        assert i_booster["recovery_date"] is None

        if "expiry_date" in i_user_booster:
            assert i_booster["expiry_date"] == i_user_booster["expiry_date"]

         
    for p_booster in purchasable_boosters:        
        p_user_booster = user_boosters[p_booster["key"]]

        assert p_booster["level"] == p_user_booster["current_level"]
        assert p_booster["next_level"] == p_user_booster["next_level"]
        assert p_booster["next_price"] == p_user_booster["next_level_price"]

    
def test_activate_interval_booster_route(client, user_id):
    interval_booster_key = 'tapping_guru'  # replace with a valid interval_booster_key

    response = client.post(f"api/v1/users/{user_id}/boosters/{interval_booster_key}/activate")

    assert response.status_code == 200
    assert isinstance(response.json(), bool)


@pytest.mark.run(after="test_add_task_bounty")
def test_claim_task_bounty(client, user_id, task_bounty_id, user_before):
    response = client.post(f'api/v1/users/{user_id}/claim-task-bounty/{task_bounty_id}', json={})
    
    assert response.status_code == 200   

    user_after = response.json()

    # Check that the user's points increased by the task bounty
    assert user_before['points'] + 1000 == user_after['points']

    
def test_activate_interval_boosters(client, user_id, user_before):
    interval_booster_keys = [list(item.keys())[0] for item in BOOSTERS['interval']]

    for interval_booster_key in interval_booster_keys:
        response = client.post(f"api/v1/users/{user_id}/boosters/{interval_booster_key}/activate")

        assert response.status_code == 200
        assert isinstance(response.json(), bool)

        user_after = client.get(f'api/v1/users/{user_id}', ).json()

        assert user_before['interval_boosters']['tapping_guru']['amount'] > user_after['interval_boosters']['tapping_guru']['amount']
