import pytest
from app.models import Ticket, Comment, User
from app import db

def test_ticket_creation_workflow(auth_client, test_user, test_project):
    """Test the complete ticket creation workflow."""
    # Create a ticket
    response = auth_client.post('/tickets/create', data={
        'title': 'Integration Test Ticket',
        'description': 'Testing the complete ticket workflow',
        'project_id': test_project.id,
        'priority': 'high',
        'status': 'open'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Ticket created successfully' in response.data
    
    # Verify ticket in database
    ticket = Ticket.query.filter_by(title='Integration Test Ticket').first()
    assert ticket is not None
    assert ticket.creator == test_user
    assert ticket.project == test_project
    
    # Clean up
    db.session.delete(ticket)
    db.session.commit()

def test_ticket_update_workflow(auth_client, test_ticket, test_user):
    """Test ticket update workflow."""
    # Update ticket
    response = auth_client.post(f'/tickets/{test_ticket.id}/edit', data={
        'title': 'Updated Ticket Title',
        'description': 'Updated ticket description',
        'priority': 'low',
        'status': 'in_progress'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Ticket updated successfully' in response.data
    
    # Verify updates
    updated_ticket = Ticket.query.get(test_ticket.id)
    assert updated_ticket.title == 'Updated Ticket Title'
    assert updated_ticket.description == 'Updated ticket description'
    assert updated_ticket.priority == 'low'
    assert updated_ticket.status == 'in_progress'

def test_ticket_assignment_workflow(auth_client, test_ticket):
    """Test ticket assignment workflow."""
    # Create a new user to assign
    assignee = User(
        username='assignee_test',
        email='assignee@test.com',
        password='password123'
    )
    db.session.add(assignee)
    db.session.commit()
    
    # Assign ticket
    response = auth_client.post(f'/tickets/{test_ticket.id}/assign', data={
        'assignee_id': assignee.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Ticket assigned successfully' in response.data
    
    # Verify assignment
    updated_ticket = Ticket.query.get(test_ticket.id)
    assert updated_ticket.assignee == assignee
    
    # Clean up
    db.session.delete(assignee)
    db.session.commit()

def test_ticket_comment_workflow(auth_client, test_ticket, test_user):
    """Test ticket commenting workflow."""
    # Add a comment
    response = auth_client.post(f'/tickets/{test_ticket.id}/comments/add', data={
        'content': 'Test comment from integration test'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Comment added successfully' in response.data
    
    # Verify comment
    comment = Comment.query.filter_by(ticket_id=test_ticket.id).first()
    assert comment is not None
    assert comment.content == 'Test comment from integration test'
    assert comment.author == test_user
    
    # Clean up
    db.session.delete(comment)
    db.session.commit()

def test_ticket_status_workflow(auth_client, test_ticket):
    """Test ticket status transition workflow."""
    status_flow = ['open', 'in_progress', 'review', 'done']
    
    for status in status_flow:
        response = auth_client.post(f'/tickets/{test_ticket.id}/status', data={
            'status': status
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Status updated successfully' in response.data
        
        # Verify status update
        updated_ticket = Ticket.query.get(test_ticket.id)
        assert updated_ticket.status == status

def test_ticket_search_workflow(auth_client, test_project, test_user):
    """Test ticket search and filtering workflow."""
    # Create test tickets with different statuses
    tickets = [
        Ticket(
            title=f'Search Test Ticket {i}',
            description=f'Test ticket {i}',
            status=status,
            priority=priority,
            project=test_project,
            creator=test_user
        )
        for i, (status, priority) in enumerate([
            ('open', 'high'),
            ('in_progress', 'medium'),
            ('done', 'low')
        ])
    ]
    db.session.add_all(tickets)
    db.session.commit()
    
    # Test status filter
    response = auth_client.get('/tickets/search?status=open')
    assert response.status_code == 200
    assert b'Search Test Ticket 0' in response.data
    assert b'Search Test Ticket 1' not in response.data
    
    # Test priority filter
    response = auth_client.get('/tickets/search?priority=high')
    assert response.status_code == 200
    assert b'Search Test Ticket 0' in response.data
    assert b'Search Test Ticket 2' not in response.data
    
    # Test text search
    response = auth_client.get('/tickets/search?q=Test ticket 1')
    assert response.status_code == 200
    assert b'Search Test Ticket 1' in response.data
    
    # Clean up
    for ticket in tickets:
        db.session.delete(ticket)
    db.session.commit()

def test_ticket_deletion_workflow(auth_client, test_ticket):
    """Test ticket deletion workflow."""
    # Add some comments to test cascade deletion
    comments = [
        Comment(
            content=f'Test comment {i}',
            ticket=test_ticket,
            author=test_ticket.creator
        )
        for i in range(2)
    ]
    db.session.add_all(comments)
    db.session.commit()
    
    # Delete ticket
    response = auth_client.post(f'/tickets/{test_ticket.id}/delete',
                              follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Ticket deleted successfully' in response.data
    
    # Verify ticket and comments are deleted
    assert Ticket.query.get(test_ticket.id) is None
    for comment in comments:
        assert Comment.query.get(comment.id) is None 