from app import app, mongo
import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register(client):
    mongo.db.users.delete_many({})

    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })

    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"
    assert mongo.db.users.find_one({'username': 'testuser'}) is not None
def test_login(client):
    mongo.db.users.insert_one({
        'username': 'loginuser',
        'password': generate_password_hash('loginpass')
    })

    response = client.post('/login', json={
        'username': 'loginuser',
        'password': 'loginpass'
    })

    assert response.status_code == 200
    assert 'access_token' in response.json
def test_analyze_text_queuing(client, mocker):
    mock_put = mocker.patch('app.task_queue.put')
    
    user_id = mongo.db.users.insert_one({
        'username': 'analyzeuser',
        'password': generate_password_hash('analyzepass')
    }).inserted_id

    login_response = client.post('/login', json={
        'username': 'analyzeuser',
        'password': 'analyzepass'
    })
    access_token = login_response.json['access_token']

    response = client.post('/analyze-text',
                           json={'text': 'Test text for analysis'},
                           headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == 202
    assert mock_put.called

