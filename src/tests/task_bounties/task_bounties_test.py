import pytest


# Task Bounties
def test_get_task_bounties(client):
    response = client.get('api/v1/task-bounties/')
    assert response.status_code == 200
    assert len(response.json()) >= 0


def test_get_task_bounty_by_id(client, task_bounty_id):
    response = client.get(f'api/v1/task-bounties/{task_bounty_id}', )
    
    assert response.status_code == 200
    assert response.json()["_id"] == task_bounty_id
