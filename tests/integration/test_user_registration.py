import pytest
from app.models import User
from app import db

def test_registration_page_loads(client):
    """Test that registration page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'Username' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data

def test_successful_registration(client, app):
    """Test successful user registration process."""
    with app.app_context():
        # Ensure user doesn't exist
        assert User.query.filter_by(email='newuser@example.com').first() is None
        
        # Submit registration
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }, follow_redirects=True)
        
        # Check response
        assert response.status_code == 200
        assert b'Registration successful' in response.data
        
        # Verify user in database
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.check_password('Password123!')
        assert user.role == 'developer'  # Default role
        
        # Clean up
        db.session.delete(user)
        db.session.commit()

def test_duplicate_email_registration(client, test_user):
    """Test registration with existing email."""
    response = client.post('/auth/register', data={
        'username': 'another_user',
        'email': test_user.email,  # Using existing email
        'password': 'Password123!',
        'password_confirm': 'Password123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_duplicate_username_registration(client, test_user):
    """Test registration with existing username."""
    response = client.post('/auth/register', data={
        'username': test_user.username,  # Using existing username
        'email': 'different@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Username already taken' in response.data

def test_invalid_registration_data(client):
    """Test registration with invalid data."""
    test_cases = [
        {
            'data': {
                'username': '',  # Empty username
                'email': 'test@example.com',
                'password': 'Password123!',
                'password_confirm': 'Password123!'
            },
            'expected_error': b'Username is required'
        },
        {
            'data': {
                'username': 'testuser',
                'email': 'invalid_email',  # Invalid email format
                'password': 'Password123!',
                'password_confirm': 'Password123!'
            },
            'expected_error': b'Invalid email address'
        },
        {
            'data': {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': '123',  # Too short password
                'password_confirm': '123'
            },
            'expected_error': b'Password must be at least 8 characters'
        },
        {
            'data': {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'Password123!',
                'password_confirm': 'DifferentPassword123!'  # Non-matching passwords
            },
            'expected_error': b'Passwords must match'
        }
    ]
    
    for test_case in test_cases:
        response = client.post('/auth/register', 
                             data=test_case['data'], 
                             follow_redirects=True)
        assert response.status_code == 200
        assert test_case['expected_error'] in response.data

def test_registration_success_redirect(client):
    """Test successful registration redirects to login page."""
    response = client.post('/auth/register', data={
        'username': 'redirectuser',
        'email': 'redirect@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!'
    })
    
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_registration_sets_session(client, app):
    """Test that successful registration sets appropriate session data."""
    with client:  # Use client context to access session
        response = client.post('/auth/register', data={
            'username': 'sessionuser',
            'email': 'session@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }, follow_redirects=True)
        
        with app.app_context():
            # Clean up the created user
            user = User.query.filter_by(email='session@example.com').first()
            if user:
                db.session.delete(user)
                db.session.commit() 