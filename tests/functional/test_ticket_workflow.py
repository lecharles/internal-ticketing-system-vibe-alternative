import pytest
from app.models import Ticket, Comment

def test_create_ticket(auth_client, test_project):
    """Test creating a new ticket."""
    response = auth_client.post('/tickets/create', data={
        'title': 'New Test Ticket',
        'description': 'This is a test ticket',
        'project_id': test_project.id,
        'priority': 'high',
        'status': 'open'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Ticket created successfully' in response.data

def test_view_ticket(auth_client, test_ticket):
    """Test viewing a ticket."""
    response = auth_client.get(f'/tickets/{test_ticket.id}')
    assert response.status_code == 200
    assert test_ticket.title.encode() in response.data
    assert test_ticket.description.encode() in response.data

def test_edit_ticket(auth_client, test_ticket):
    """Test editing a ticket."""
    response = auth_client.post(f'/tickets/{test_ticket.id}/edit', data={
        'title': 'Updated Ticket Title',
        'description': 'Updated description',
        'priority': 'low',
        'status': 'in_progress'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Ticket updated successfully' in response.data
    assert b'Updated Ticket Title' in response.data

def test_ticket_workflow(auth_client, test_ticket):
    """Test ticket status workflow."""
    # Change status to in progress
    response = auth_client.post(f'/tickets/{test_ticket.id}/status', data={
        'status': 'in_progress'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'in_progress' in response.data

    # Change status to done
    response = auth_client.post(f'/tickets/{test_ticket.id}/status', data={
        'status': 'done'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'done' in response.data

def test_add_comment(auth_client, test_ticket):
    """Test adding a comment to a ticket."""
    response = auth_client.post(f'/tickets/{test_ticket.id}/comment', data={
        'content': 'This is a test comment'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Comment added successfully' in response.data
    assert b'This is a test comment' in response.data

def test_ticket_listing(auth_client, test_ticket):
    """Test ticket listing page."""
    response = auth_client.get('/tickets/')
    assert response.status_code == 200
    assert test_ticket.title.encode() in response.data

def test_ticket_filtering(auth_client, test_ticket):
    """Test ticket filtering."""
    # Filter by status
    response = auth_client.get('/tickets/?status=open')
    assert response.status_code == 200
    assert test_ticket.title.encode() in response.data

    # Filter by priority
    response = auth_client.get('/tickets/?priority=medium')
    assert response.status_code == 200
    assert test_ticket.title.encode() in response.data 