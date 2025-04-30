import pytest
from datetime import datetime
from app.models import User, Ticket, Comment
from app import db

def test_new_user(test_user):
    """Test creating a new user."""
    assert test_user.username == 'testuser'
    assert test_user.email == 'test@example.com'
    assert test_user.password_hash is not None
    assert not test_user.password_hash == 'testpass123'
    assert test_user.role == 'developer'  # Default role
    assert isinstance(test_user.created_at, datetime)

def test_password_hashing(test_user):
    """Test password hashing and verification."""
    assert test_user.check_password('testpass123')
    assert not test_user.check_password('wrongpass')
    
    # Test setting new password
    test_user.set_password('newpass123')
    assert test_user.check_password('newpass123')
    assert not test_user.check_password('testpass123')

def test_user_representation(test_user):
    """Test string representation of user."""
    assert str(test_user) == '<User testuser>'

def test_user_roles(app):
    """Test user role assignment and validation."""
    with app.app_context():
        # Test explicit role assignment
        user = User(username='roleuser', email='role@test.com', role='admin')
        user.set_password('pass123')
        db.session.add(user)
        db.session.commit()
        assert user.role == 'admin'
        
        # Test default role
        default_user = User(username='defaultuser', email='default@test.com')
        default_user.set_password('pass123')
        db.session.add(default_user)
        db.session.commit()
        assert default_user.role == 'developer'

def test_unique_constraints(app, test_user):
    """Test unique constraints on username and email."""
    with app.app_context():
        # Try to create user with same username
        duplicate_username = User(username='testuser', email='different@example.com')
        duplicate_username.set_password('pass123')
        with pytest.raises(Exception):
            db.session.add(duplicate_username)
            db.session.commit()
        db.session.rollback()
        
        # Try to create user with same email
        duplicate_email = User(username='different', email='test@example.com')
        duplicate_email.set_password('pass123')
        with pytest.raises(Exception):
            db.session.add(duplicate_email)
            db.session.commit()
        db.session.rollback()

def test_user_ticket_relationships(app, test_user):
    """Test user relationships with tickets."""
    with app.app_context():
        # Create a project for the tickets
        from app.models import Project
        project = Project(name='Test Project', description='Test Description')
        db.session.add(project)
        db.session.commit()
        
        # Create tickets assigned to and created by the user
        ticket1 = Ticket(
            title='Test Ticket 1',
            description='Test Description',
            project=project,
            creator=test_user,
            assignee=test_user
        )
        ticket2 = Ticket(
            title='Test Ticket 2',
            description='Test Description',
            project=project,
            creator=test_user
        )
        db.session.add_all([ticket1, ticket2])
        db.session.commit()
        
        # Test relationships
        assert ticket1 in test_user.assigned_tickets
        assert ticket1 in test_user.created_tickets
        assert ticket2 in test_user.created_tickets
        assert ticket2 not in test_user.assigned_tickets
        
        # Test relationship counts
        assert test_user.assigned_tickets.count() == 1
        assert test_user.created_tickets.count() == 2

def test_user_comment_relationship(app, test_user):
    """Test user relationship with comments."""
    with app.app_context():
        # Create necessary related objects
        project = Project(name='Test Project', description='Test Description')
        db.session.add(project)
        db.session.commit()
        
        ticket = Ticket(
            title='Test Ticket',
            description='Test Description',
            project=project,
            creator=test_user
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Create comments by the user
        comment1 = Comment(
            content='Test Comment 1',
            ticket=ticket,
            author=test_user
        )
        comment2 = Comment(
            content='Test Comment 2',
            ticket=ticket,
            author=test_user
        )
        db.session.add_all([comment1, comment2])
        db.session.commit()
        
        # Test relationship
        assert comment1 in test_user.comments
        assert comment2 in test_user.comments
        assert test_user.comments.count() == 2

def test_invalid_username_registration(app):
    """Test invalid username registration."""
    with app.app_context():
        # Test empty username
        with pytest.raises(Exception):
            user = User(username='', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        db.session.rollback()
        
        # Test None username
        with pytest.raises(Exception):
            user = User(username=None, email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        db.session.rollback()

def test_invalid_email_registration(app):
    """Test invalid email registration."""
    with app.app_context():
        # Test invalid email format
        with pytest.raises(Exception):
            user = User(username='testuser', email='invalid-email')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        db.session.rollback()
        
        # Test empty email
        with pytest.raises(Exception):
            user = User(username='testuser', email='')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        db.session.rollback()
        
        # Test None email
        with pytest.raises(Exception):
            user = User(username='testuser', email=None)
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        db.session.rollback() 