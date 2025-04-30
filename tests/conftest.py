import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Project, Ticket, Comment, Team

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app('testing')
    
    # Add test configuration
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    return app

@pytest.fixture(scope='function')
def _db(app):
    """Create the database."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(_db):
    """Create a new database session for a test."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    
    session = _db.session
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username='test_user',
        email='test@example.com',
        role='developer'
    )
    user.set_password('test_password')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('adminpass123')
    db_session.add(admin)
    db_session.commit()
    yield admin
    # Clean up
    db_session.delete(admin)
    db_session.commit()

@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project."""
    project = Project(
        name='Test Project',
        description='A test project',
        creator_id=test_user.id
    )
    db_session.add(project)
    db_session.commit()
    return project

@pytest.fixture
def test_ticket(db_session, test_project, test_user):
    """Create a test ticket."""
    ticket = Ticket(
        title='Test Ticket',
        description='A test ticket',
        project=test_project,
        creator=test_user,
        status='open',
        priority='medium'
    )
    db_session.add(ticket)
    db_session.commit()
    yield ticket
    
    # Cleanup
    db_session.delete(ticket)
    db_session.commit()

@pytest.fixture
def test_comment(db_session, test_user, test_ticket):
    """Create a test comment."""
    comment = Comment(
        content='Test comment content',
        ticket=test_ticket,
        author=test_user
    )
    db_session.add(comment)
    db_session.commit()
    yield comment
    # Clean up
    db_session.delete(comment)
    db_session.commit()

@pytest.fixture
def auth_client(client, test_user):
    """A test client with authentication."""
    with client:
        client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'test_password'
        }, follow_redirects=True)
        yield client

@pytest.fixture
def test_team(db_session, test_user):
    """Create a test team."""
    team = Team(
        name='Test Team',
        description='A test team',
        leader=test_user
    )
    db_session.add(team)
    db_session.commit()
    yield team
    
    # Clean up
    db_session.delete(team)
    db_session.commit() 