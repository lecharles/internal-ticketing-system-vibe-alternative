import os
import pytest
from app import create_app, db
from app.models import User, Project, Ticket, Comment

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary database file
    test_db = "postgresql://localhost/internal_ticketing_test"
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': test_db,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False  # Disable CSRF tokens in tests
    })

    # Create the database and tables
    with app.app_context():
        db.create_all()
        yield app
        # Clean up after the test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """A test client with authentication."""
    with client:
        # Create and log in a test user
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }, follow_redirects=True)
        yield client
        # Clean up after the test
        with client.application.app_context():
            User.query.filter_by(username='testuser').delete()
            db.session.commit()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        yield user
        # Clean up
        db.session.delete(user)
        db.session.commit()

@pytest.fixture
def test_project(app, test_user):
    """Create a test project."""
    with app.app_context():
        project = Project(
            name='Test Project',
            description='A test project',
            created_by=test_user.id
        )
        db.session.add(project)
        db.session.commit()
        yield project
        # Clean up
        db.session.delete(project)
        db.session.commit()

@pytest.fixture
def test_ticket(app, test_user, test_project):
    """Create a test ticket."""
    with app.app_context():
        ticket = Ticket(
            title='Test Ticket',
            description='A test ticket',
            status='open',
            priority='medium',
            project_id=test_project.id,
            created_by=test_user.id,
            assigned_to=test_user.id
        )
        db.session.add(ticket)
        db.session.commit()
        yield ticket
        # Clean up
        db.session.delete(ticket)
        db.session.commit() 