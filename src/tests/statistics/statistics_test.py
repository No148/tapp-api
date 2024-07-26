# Stats
def test_get_stats(client):
    response = client.get('api/v1/statistics/')

    assert response.status_code == 200