import pytest
from flask import session
from app.models import User
from app import db

def test_login_page_loads(client):
    """Test that login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data

def test_successful_login(client, test_user):
    """Test successful login process."""
    response = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert test_user.username.encode() in response.data

def test_login_with_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    # Test with wrong password
    response = client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data
    
    # Test with non-existent email
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_login_validation(client):
    """Test login form validation."""
    test_cases = [
        {
            'data': {
                'email': '',  # Empty email
                'password': 'testpass123'
            },
            'expected_error': b'Email is required'
        },
        {
            'data': {
                'email': 'invalid_email',  # Invalid email format
                'password': 'testpass123'
            },
            'expected_error': b'Invalid email address'
        },
        {
            'data': {
                'email': 'test@example.com',
                'password': ''  # Empty password
            },
            'expected_error': b'Password is required'
        }
    ]
    
    for test_case in test_cases:
        response = client.post('/auth/login', 
                             data=test_case['data'], 
                             follow_redirects=True)
        assert response.status_code == 200
        assert test_case['expected_error'] in response.data

def test_logout(auth_client):
    """Test logout functionality."""
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    # Verify session is cleared
    assert 'user_id' not in session

def test_login_session(client, test_user):
    """Test session handling during login."""
    with client:  # Use client context to access session
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'user_id' in session
        assert session['user_id'] == test_user.id

def test_remember_me_functionality(client, test_user):
    """Test remember me functionality."""
    with client:
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'testpass123',
            'remember_me': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check for remember_me cookie
        assert 'remember_token' in response.headers.get('Set-Cookie', '')

def test_access_protected_route(client, auth_client):
    """Test accessing protected routes with and without authentication."""
    # Test without authentication
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page' in response.data
    
    # Test with authentication
    response = auth_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_redirect(client):
    """Test redirect after login."""
    # Try to access protected page
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location
    
    # Verify next parameter is set
    response = client.get('/auth/login')
    assert b'next=' in response.data 