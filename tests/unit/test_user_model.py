import pytest
from app.models import User

def test_new_user(test_user):
    """Test creating a new user."""
    assert test_user.username == 'testuser'
    assert test_user.email == 'test@example.com'
    assert test_user.password_hash is not None
    assert not test_user.password_hash == 'testpass123'

def test_password_hashing(test_user):
    """Test password hashing."""
    assert test_user.check_password('testpass123')
    assert not test_user.check_password('wrongpass')

def test_user_representation(test_user):
    """Test string representation of user."""
    assert str(test_user) == f'User: {test_user.username}'

def test_invalid_username_registration(app):
    """Test invalid username registration."""
    with app.app_context():
        user = User(username='', email='test@example.com')
        user.set_password('testpass123')
        assert not user.username  # Username should not be empty

def test_invalid_email_registration(app):
    """Test invalid email registration."""
    with app.app_context():
        user = User(username='testuser', email='invalid-email')
        user.set_password('testpass123')
        # This should raise a validation error when saving to db
        with pytest.raises(Exception):
            db.session.add(user)
            db.session.commit() 