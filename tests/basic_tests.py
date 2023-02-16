import pytest
import requests

LOCAL_SERVER_PORT = 5000
BCO_SERVER_ADDRESS = 'http://ha:13781/graphql'
CLOUD_SERVER_ADDRESS = 'https://<cloud_server_ip>'
AUTH_TOKEN = '<insert_auth_token_here>'

@pytest.fixture(scope='session')
def api_url():
    return f'http://localhost:{LOCAL_SERVER_PORT}'

def test_get_devices(api_url):
    response = requests.get(f'{api_url}/devices', headers={'Authorization': AUTH_TOKEN})
    assert response.status_code == 200
    assert response.json() is not None

def test_get_rooms(api_url):
    response = requests.get(f'{api_url}/rooms', headers={'Authorization': AUTH_TOKEN})
    assert response.status_code == 200
    assert response.json() is not None

def test_get_scenes(api_url):
    response = requests.get(f'{api_url}/scenes', headers={'Authorization': AUTH_TOKEN})
    assert response.status_code == 200
    assert response.json() is not None

def test_unauthorized_request(api_url):
    response = requests.get(f'{api_url}/devices')
    assert response.status_code == 401
    assert response.json() == {'message': 'Unauthorized'}
