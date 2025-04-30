import pytest
from flask import url_for
from app.models import Ticket, Comment, User, Project, Team
from app.errors.exceptions import ResourceNotFoundError, AuthorizationError

def test_delete_ticket_success(test_client, auth, test_db):
    """Test successful ticket deletion by creator."""
    # Create a user and log them in
    user = User(username='testuser', email='test@example.com', password='Test123!')
    test_db.session.add(user)
    test_db.session.commit()
    auth.login('testuser', 'Test123!')
    
    # Create a ticket
    project = Project(name='Test Project')
    test_db.session.add(project)
    ticket = Ticket(
        title='Test Ticket',
        description='Test Description',
        project=project,
        creator_id=user.id
    )
    test_db.session.add(ticket)
    comment = Comment(
        content='Test Comment',
        ticket=ticket,
        author_id=user.id
    )
    test_db.session.add(comment)
    test_db.session.commit()
    
    # Delete the ticket
    response = test_client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302
    assert response.headers['Location'] == url_for('tickets.list', _external=True)
    
    # Verify ticket and comments are deleted
    assert Ticket.query.get(ticket.id) is None
    assert Comment.query.filter_by(ticket_id=ticket.id).first() is None

def test_delete_ticket_as_admin(test_client, auth, test_db):
    """Test successful ticket deletion by admin."""
    # Create users
    creator = User(username='creator', email='creator@example.com', password='Test123!')
    admin = User(username='admin', email='admin@example.com', password='Test123!', role='admin')
    test_db.session.add_all([creator, admin])
    test_db.session.commit()
    
    # Create a ticket
    project = Project(name='Test Project')
    test_db.session.add(project)
    ticket = Ticket(
        title='Test Ticket',
        description='Test Description',
        project=project,
        creator_id=creator.id
    )
    test_db.session.add(ticket)
    test_db.session.commit()
    
    # Login as admin and delete the ticket
    auth.login('admin', 'Test123!')
    response = test_client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302
    assert Ticket.query.get(ticket.id) is None

def test_delete_ticket_as_team_lead(test_client, auth, test_db):
    """Test successful ticket deletion by team lead."""
    # Create users
    creator = User(username='creator', email='creator@example.com', password='Test123!')
    team_lead = User(username='lead', email='lead@example.com', password='Test123!')
    test_db.session.add_all([creator, team_lead])
    test_db.session.commit()
    
    # Create team and project
    team = Team(name='Test Team', leader=team_lead)
    project = Project(name='Test Project', team=team)
    test_db.session.add_all([team, project])
    test_db.session.commit()
    
    # Create a ticket
    ticket = Ticket(
        title='Test Ticket',
        description='Test Description',
        project=project,
        creator_id=creator.id
    )
    test_db.session.add(ticket)
    test_db.session.commit()
    
    # Login as team lead and delete the ticket
    auth.login('lead', 'Test123!')
    response = test_client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302
    assert Ticket.query.get(ticket.id) is None

def test_delete_nonexistent_ticket(test_client, auth, test_db):
    """Test attempt to delete a nonexistent ticket."""
    # Create and login user
    user = User(username='testuser', email='test@example.com', password='Test123!')
    test_db.session.add(user)
    test_db.session.commit()
    auth.login('testuser', 'Test123!')
    
    # Attempt to delete nonexistent ticket
    response = test_client.post('/tickets/999/delete')
    assert response.status_code == 302
    assert response.headers['Location'] == url_for('tickets.list', _external=True)

def test_delete_ticket_unauthorized(test_client, auth, test_db):
    """Test attempt to delete ticket without proper authorization."""
    # Create users
    creator = User(username='creator', email='creator@example.com', password='Test123!')
    other_user = User(username='other', email='other@example.com', password='Test123!')
    test_db.session.add_all([creator, other_user])
    test_db.session.commit()
    
    # Create a ticket
    project = Project(name='Test Project')
    test_db.session.add(project)
    ticket = Ticket(
        title='Test Ticket',
        description='Test Description',
        project=project,
        creator_id=creator.id
    )
    test_db.session.add(ticket)
    test_db.session.commit()
    
    # Login as other user and attempt to delete
    auth.login('other', 'Test123!')
    response = test_client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302
    assert response.headers['Location'] == url_for('tickets.view', ticket_id=ticket.id, _external=True)
    assert Ticket.query.get(ticket.id) is not None  # Ticket should still exist

def test_delete_ticket_unauthenticated(test_client, test_db):
    """Test attempt to delete ticket without authentication."""
    # Create a ticket
    user = User(username='creator', email='creator@example.com', password='Test123!')
    test_db.session.add(user)
    project = Project(name='Test Project')
    test_db.session.add(project)
    ticket = Ticket(
        title='Test Ticket',
        description='Test Description',
        project=project,
        creator_id=user.id
    )
    test_db.session.add(ticket)
    test_db.session.commit()
    
    # Attempt to delete without login
    response = test_client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302
    assert 'login' in response.headers['Location']
    assert Ticket.query.get(ticket.id) is not None  # Ticket should still exist 