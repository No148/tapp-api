import pytest


# Referrals
def test_create_referrals(client, user_id):
    referral_id = 99999999
    data = {"referrer_id": user_id, "referral_id": referral_id}
    
    response = client.post('api/v1/referrals/', json=data)
    
    assert response.status_code == 200
    assert response.json()["referrer_id"] == user_id
    assert response.json()["referral_id"] == referral_id


@pytest.mark.run(after="test_create_referrals")
def test_get_referrals(client, user_id):
    response = client.get(f'api/v1/referrals/?referrer_id={user_id}')

    assert response.status_code == 200
    assert len(response.json()) >= 0