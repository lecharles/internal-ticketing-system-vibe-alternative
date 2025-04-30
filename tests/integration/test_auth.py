import pytest
from flask import session
from app.models import User

def test_register(client):
    """Test user registration."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123',
        'password_confirm': 'newpass123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_login_logout(auth_client):
    """Test login and logout functionality."""
    # Test login
    response = auth_client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful' in response.data

    # Test logout
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_invalid_login(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_protected_routes(client, auth_client):
    """Test access to protected routes."""
    # Without authentication
    response = client.get('/tickets/create')
    assert response.status_code == 302  # Redirect to login

    # With authentication
    response = auth_client.get('/tickets/create')
    assert response.status_code == 200
    assert b'Create Ticket' in response.data

def test_duplicate_registration(client, test_user):
    """Test registration with existing email."""
    response = client.post('/auth/register', data={
        'username': 'another',
        'email': 'test@example.com',  # Same email as test_user
        'password': 'anotherpass123',
        'password_confirm': 'anotherpass123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email already registered' in response.data 