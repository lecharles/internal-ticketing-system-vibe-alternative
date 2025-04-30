import pytest
from datetime import datetime
from app.models import Project, Ticket
from app import db

def test_new_project(test_project):
    """Test creating a new project."""
    assert test_project.name == 'Test Project'
    assert test_project.description == 'A test project'
    assert isinstance(test_project.created_at, datetime)

def test_project_representation(test_project):
    """Test string representation of project."""
    assert str(test_project) == '<Project Test Project>'

def test_project_ticket_relationship(app, test_project, test_user):
    """Test project relationship with tickets."""
    with app.app_context():
        # Create multiple tickets for the project
        ticket1 = Ticket(
            title='Test Ticket 1',
            description='Test Description 1',
            project=test_project,
            creator=test_user
        )
        ticket2 = Ticket(
            title='Test Ticket 2',
            description='Test Description 2',
            project=test_project,
            creator=test_user
        )
        db.session.add_all([ticket1, ticket2])
        db.session.commit()

        # Test relationships
        assert ticket1 in test_project.tickets
        assert ticket2 in test_project.tickets
        assert test_project.tickets.count() == 2

        # Test cascade delete
        db.session.delete(test_project)
        db.session.commit()
        
        # Verify tickets are deleted
        assert Ticket.query.filter_by(id=ticket1.id).first() is None
        assert Ticket.query.filter_by(id=ticket2.id).first() is None

def test_invalid_project_creation(app):
    """Test invalid project creation scenarios."""
    with app.app_context():
        # Test empty name
        with pytest.raises(Exception):
            project = Project(name='', description='Test Description')
            db.session.add(project)
            db.session.commit()
        db.session.rollback()

        # Test None name
        with pytest.raises(Exception):
            project = Project(name=None, description='Test Description')
            db.session.add(project)
            db.session.commit()
        db.session.rollback()

def test_project_timestamps(app):
    """Test project timestamps are set correctly."""
    with app.app_context():
        # Create a new project
        project = Project(name='Timestamp Test', description='Testing timestamps')
        db.session.add(project)
        db.session.commit()

        # Verify created_at is set
        assert isinstance(project.created_at, datetime)
        assert (datetime.utcnow() - project.created_at).total_seconds() < 10  # Within 10 seconds

        # Clean up
        db.session.delete(project)
        db.session.commit()

def test_project_description_optional(app):
    """Test that project description is optional."""
    with app.app_context():
        # Create project without description
        project = Project(name='No Description Project')
        db.session.add(project)
        db.session.commit()

        assert project.description is None

        # Clean up
        db.session.delete(project)
        db.session.commit()

def test_project_name_unique_constraint(app, test_project):
    """Test that project names must be unique."""
    with app.app_context():
        # Try to create project with same name
        duplicate_project = Project(name='Test Project', description='Another project')
        db.session.add(duplicate_project)
        
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

def test_project_name_validation(app):
    """Test project name validation rules."""
    with app.app_context():
        # Test name too long (assuming max length is 100)
        with pytest.raises(Exception):
            project = Project(name='x' * 101, description='Test Description')
            db.session.add(project)
            db.session.commit()
        db.session.rollback()

        # Test name with invalid characters
        with pytest.raises(Exception):
            project = Project(name='Invalid/Project\\Name', description='Test Description')
            db.session.add(project)
            db.session.commit()
        db.session.rollback()

def test_project_update_operations(app, test_project):
    """Test project update operations."""
    with app.app_context():
        # Update project name
        test_project.name = 'Updated Project Name'
        test_project.description = 'Updated description'
        db.session.commit()

        # Verify updates
        updated_project = Project.query.get(test_project.id)
        assert updated_project.name == 'Updated Project Name'
        assert updated_project.description == 'Updated description'

def test_project_archival(app, test_project):
    """Test project archival functionality."""
    with app.app_context():
        # Archive project
        test_project.is_archived = True
        test_project.archived_at = datetime.utcnow()
        db.session.commit()

        # Verify archival
        archived_project = Project.query.get(test_project.id)
        assert archived_project.is_archived is True
        assert isinstance(archived_project.archived_at, datetime)

        # Test that archived projects don't accept new tickets
        with pytest.raises(Exception):
            ticket = Ticket(
                title='New Ticket',
                description='Should not be allowed',
                project=test_project,
                creator=test_user
            )
            db.session.add(ticket)
            db.session.commit()
        db.session.rollback() 