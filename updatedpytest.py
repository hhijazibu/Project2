import pytest
from werkzeug.security import generate_password_hash
from app import app, mongo


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_register(client):
    """Test user registration."""
    mongo.db.users.delete_many({})

    # Test valid registration
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful, please login.' in response.data
    assert mongo.db.users.find_one({'username': 'testuser'}) is not None

    # Test duplicate registration
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    assert b'Username already exists' in response.data

def test_login(client):
    """Test user login."""
    hashed_password = generate_password_hash('loginpass')
    mongo.db.users.insert_one({
        'username': 'loginuser',
        'password': hashed_password
    })

    # Test successful login
    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'loginpass'
    }, follow_redirects=True)

    assert b'Upload successful, processing started.' in response.data

    # Test unsuccessful login
    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'wrongpass'
    }, follow_redirects=True)

    assert b'Invalid username or password' in response.data

def test_analyze_text_queuing(client, mocker):
    """Test text analysis queuing."""
    mock_put = mocker.patch('queue.Queue.put')
    user_id = mongo.db.users.insert_one({
        'username': 'analyzeuser',
        'password': generate_password_hash('analyzepass')
    }).inserted_id

    client.post('/login', data={
        'username': 'analyzeuser',
        'password': 'analyzepass'
    }, follow_redirects=True)

    response = client.post('/upload', data={
        'file': (BytesIO(b'some text contents'), 'test.txt')
    }, content_type='multipart/form-data')

    assert response.status_code == 200
    assert mock_put.called
