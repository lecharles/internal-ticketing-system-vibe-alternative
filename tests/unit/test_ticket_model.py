import pytest
from datetime import datetime
from app.models import Ticket, Comment, User
from app import db

def test_new_ticket(test_ticket):
    """Test creating a new ticket."""
    assert test_ticket.title == 'Test Ticket'
    assert test_ticket.description == 'A test ticket'
    assert isinstance(test_ticket.created_at, datetime)
    assert test_ticket.status == 'open'
    assert test_ticket.priority == 'medium'

def test_ticket_representation(test_ticket):
    """Test string representation of ticket."""
    assert str(test_ticket) == '<Ticket Test Ticket>'

def test_ticket_relationships(app, test_ticket, test_project, test_user):
    """Test ticket relationships with project, creator, and assignee."""
    with app.app_context():
        assert test_ticket.project == test_project
        assert test_ticket.creator == test_user
        
        # Test assignee
        assignee = User(
            username='assignee',
            email='assignee@example.com',
            password='password123'
        )
        db.session.add(assignee)
        db.session.commit()
        
        test_ticket.assignee = assignee
        db.session.commit()
        
        assert test_ticket.assignee == assignee

def test_ticket_comments(app, test_ticket, test_user):
    """Test ticket relationship with comments."""
    with app.app_context():
        # Create comments
        comment1 = Comment(
            content='Test Comment 1',
            ticket=test_ticket,
            author=test_user
        )
        comment2 = Comment(
            content='Test Comment 2',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add_all([comment1, comment2])
        db.session.commit()

        # Test relationships
        assert comment1 in test_ticket.comments
        assert comment2 in test_ticket.comments
        assert test_ticket.comments.count() == 2

        # Test cascade delete
        db.session.delete(test_ticket)
        db.session.commit()
        
        # Verify comments are deleted
        assert Comment.query.filter_by(id=comment1.id).first() is None
        assert Comment.query.filter_by(id=comment2.id).first() is None

def test_invalid_ticket_creation(app, test_project, test_user):
    """Test invalid ticket creation scenarios."""
    with app.app_context():
        # Test empty title
        with pytest.raises(Exception):
            ticket = Ticket(
                title='',
                description='Test Description',
                project=test_project,
                creator=test_user
            )
            db.session.add(ticket)
            db.session.commit()
        db.session.rollback()

        # Test invalid status
        with pytest.raises(Exception):
            ticket = Ticket(
                title='Test Ticket',
                description='Test Description',
                status='invalid_status',
                project=test_project,
                creator=test_user
            )
            db.session.add(ticket)
            db.session.commit()
        db.session.rollback()

        # Test invalid priority
        with pytest.raises(Exception):
            ticket = Ticket(
                title='Test Ticket',
                description='Test Description',
                priority='invalid_priority',
                project=test_project,
                creator=test_user
            )
            db.session.add(ticket)
            db.session.commit()
        db.session.rollback()

def test_ticket_timestamps(app, test_project, test_user):
    """Test ticket timestamps are set correctly."""
    with app.app_context():
        ticket = Ticket(
            title='Timestamp Test',
            description='Testing timestamps',
            project=test_project,
            creator=test_user
        )
        db.session.add(ticket)
        db.session.commit()

        # Verify created_at is set
        assert isinstance(ticket.created_at, datetime)
        assert (datetime.utcnow() - ticket.created_at).total_seconds() < 10

        # Test updated_at on modification
        original_updated_at = ticket.updated_at
        ticket.description = 'Updated description'
        db.session.commit()
        
        assert ticket.updated_at > original_updated_at

        # Clean up
        db.session.delete(ticket)
        db.session.commit()

def test_ticket_status_transitions(app, test_ticket):
    """Test valid ticket status transitions."""
    with app.app_context():
        # Test valid transitions
        valid_statuses = ['open', 'in_progress', 'review', 'done']
        
        for status in valid_statuses:
            test_ticket.status = status
            db.session.commit()
            assert test_ticket.status == status

def test_ticket_search_by_status(app, test_project, test_user):
    """Test searching tickets by status."""
    with app.app_context():
        # Create tickets with different statuses
        tickets = [
            Ticket(title=f'Ticket {i}', 
                  description=f'Description {i}',
                  status=status,
                  project=test_project,
                  creator=test_user)
            for i, status in enumerate(['open', 'in_progress', 'done'])
        ]
        db.session.add_all(tickets)
        db.session.commit()

        # Test filtering
        assert Ticket.query.filter_by(status='open').count() == 1
        assert Ticket.query.filter_by(status='in_progress').count() == 1
        assert Ticket.query.filter_by(status='done').count() == 1

        # Clean up
        for ticket in tickets:
            db.session.delete(ticket)
        db.session.commit() 