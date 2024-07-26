# Configs
def test_get_configs(client):
    response = client.get('api/v1/configs/')
    
    assert response.status_code == 200
