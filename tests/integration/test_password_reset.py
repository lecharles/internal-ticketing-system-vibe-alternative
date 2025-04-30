import pytest
from flask import url_for
from app.models import User
from app import db

def test_reset_password_request_page(client):
    """Test that reset password request page loads correctly."""
    response = client.get('/auth/reset-password-request')
    assert response.status_code == 200
    assert b'Reset Your Password' in response.data
    assert b'Email' in response.data

def test_reset_password_request_with_invalid_email(client):
    """Test reset password request with non-existent email."""
    response = client.post('/auth/reset-password-request', data={
        'email': 'nonexistent@example.com'
    })
    assert b'No account found with that email address' in response.data

def test_reset_password_request_with_valid_email(client, test_user):
    """Test reset password request with valid email."""
    response = client.post('/auth/reset-password-request', data={
        'email': test_user.email
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Check your email for instructions' in response.data
    
    # Verify token was generated
    user = User.query.filter_by(email=test_user.email).first()
    assert user.reset_token is not None
    assert user.reset_token_expiry is not None

def test_reset_password_with_invalid_token(client):
    """Test reset password with invalid token."""
    response = client.get('/auth/reset-password/invalid-token', follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid or expired reset token' in response.data

def test_reset_password_with_expired_token(client, test_user):
    """Test reset password with expired token."""
    from datetime import datetime, timedelta
    
    # Generate token but set it as expired
    token = test_user.generate_reset_token()
    test_user.reset_token_expiry = datetime.utcnow() - timedelta(hours=2)
    db.session.commit()
    
    response = client.get(f'/auth/reset-password/{token}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid or expired reset token' in response.data

def test_successful_password_reset(client, test_user):
    """Test successful password reset flow."""
    # Generate reset token
    token = test_user.generate_reset_token()
    
    # Access reset password page
    response = client.get(f'/auth/reset-password/{token}')
    assert response.status_code == 200
    assert b'Set New Password' in response.data
    
    # Submit new password
    response = client.post(f'/auth/reset-password/{token}', data={
        'password': 'newpassword123',
        'password_confirm': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your password has been reset' in response.data
    
    # Verify password was changed
    user = User.query.filter_by(email=test_user.email).first()
    assert user.check_password('newpassword123')
    
    # Verify token was cleared
    assert user.reset_token is None
    assert user.reset_token_expiry is None

def test_reset_password_validation(client, test_user):
    """Test password reset validation."""
    token = test_user.generate_reset_token()
    
    test_cases = [
        {
            'data': {
                'password': 'short',
                'password_confirm': 'short'
            },
            'expected_error': b'Password must be at least 6 characters long'
        },
        {
            'data': {
                'password': 'password123',
                'password_confirm': 'differentpassword'
            },
            'expected_error': b'Passwords must match'
        }
    ]
    
    for test_case in test_cases:
        response = client.post(f'/auth/reset-password/{token}',
                             data=test_case['data'],
                             follow_redirects=True)
        assert response.status_code == 200
        assert test_case['expected_error'] in response.data 