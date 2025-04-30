import pytest
from app.models import Ticket, Comment, User, Project
from app import db

def test_ticket_deletion(client, auth_client, test_user, test_project):
    """Test the ticket deletion workflow with various scenarios."""
    # Create a test ticket
    ticket = Ticket(
        title='Test Ticket for Deletion',
        description='This ticket will be deleted',
        status='open',
        priority='medium',
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.session.add(ticket)
    db.session.commit()

    # Test 1: Unauthorized user cannot delete ticket
    client.get('/auth/logout')  # Ensure logged out
    response = client.post(f'/tickets/{ticket.id}/delete')
    assert response.status_code == 302  # Redirects to login
    assert Ticket.query.get(ticket.id) is not None  # Ticket still exists

    # Test 2: Non-creator user cannot delete ticket
    other_user = User(username='other_user', email='other@example.com', role='developer')
    other_user.set_password('password123')
    db.session.add(other_user)
    db.session.commit()
    
    with auth_client.session_transaction() as sess:
        sess['user_id'] = other_user.id
    
    response = auth_client.post(f'/tickets/{ticket.id}/delete', follow_redirects=True)
    assert b'You do not have permission to delete this ticket' in response.data
    assert Ticket.query.get(ticket.id) is not None  # Ticket still exists

    # Test 3: Creator can successfully delete ticket
    with auth_client.session_transaction() as sess:
        sess['user_id'] = test_user.id
    
    response = auth_client.post(f'/tickets/{ticket.id}/delete', follow_redirects=True)
    assert b'Ticket deleted successfully' in response.data
    assert Ticket.query.get(ticket.id) is None  # Ticket is deleted

    # Test 4: Admin can delete any ticket
    # Create another ticket
    ticket2 = Ticket(
        title='Admin Delete Test',
        description='This ticket will be deleted by admin',
        status='open',
        priority='medium',
        project_id=test_project.id,
        creator_id=other_user.id
    )
    db.session.add(ticket2)
    db.session.commit()

    # Make test_user an admin
    test_user.role = 'admin'
    db.session.commit()

    response = auth_client.post(f'/tickets/{ticket2.id}/delete', follow_redirects=True)
    assert b'Ticket deleted successfully' in response.data
    assert Ticket.query.get(ticket2.id) is None  # Ticket is deleted

    # Test 5: Deleting non-existent ticket
    response = auth_client.post('/tickets/99999/delete', follow_redirects=True)
    assert response.status_code == 404

    # Cleanup
    db.session.delete(other_user)
    db.session.commit() 