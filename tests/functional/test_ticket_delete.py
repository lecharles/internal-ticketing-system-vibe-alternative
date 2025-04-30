import pytest
from flask_login import current_user
from app.models import Ticket, Comment, User
from app import db

def test_ticket_delete_by_creator(auth_client, test_ticket, test_user):
    """Test ticket deletion by its creator."""
    with auth_client:
        # Login as ticket creator
        auth_client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123'
        })
        
        # Try to delete the ticket
        response = auth_client.post(f'/tickets/{test_ticket.id}/delete',
                                  follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Ticket deleted successfully' in response.data
        assert Ticket.query.get(test_ticket.id) is None

def test_ticket_delete_by_admin(app, auth_client, test_ticket, test_admin):
    """Test ticket deletion by an admin."""
    with auth_client:
        # Login as admin
        auth_client.post('/auth/login', data={
            'email': test_admin.email,
            'password': 'adminpass123'
        })
        
        # Try to delete the ticket
        response = auth_client.post(f'/tickets/{test_ticket.id}/delete',
                                  follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Ticket deleted successfully' in response.data
        assert Ticket.query.get(test_ticket.id) is None

def test_ticket_delete_unauthorized(app, auth_client, test_ticket):
    """Test ticket deletion by unauthorized user."""
    with app.app_context():
        # Create another regular user
        unauthorized_user = User(
            username='unauthorized',
            email='unauthorized@example.com'
        )
        unauthorized_user.set_password('password123')
        db.session.add(unauthorized_user)
        db.session.commit()
        
        with auth_client:
            # Login as unauthorized user
            auth_client.post('/auth/login', data={
                'email': unauthorized_user.email,
                'password': 'password123'
            })
            
            # Try to delete the ticket
            response = auth_client.post(f'/tickets/{test_ticket.id}/delete',
                                      follow_redirects=True)
            
            assert response.status_code == 200
            assert b'You do not have permission to delete this ticket' in response.data
            assert Ticket.query.get(test_ticket.id) is not None
        
        # Clean up
        db.session.delete(unauthorized_user)
        db.session.commit()

def test_ticket_delete_with_comments(app, auth_client, test_ticket, test_user):
    """Test that deleting a ticket also deletes its comments."""
    with app.app_context():
        # Add some comments to the ticket
        comments = []
        for i in range(3):
            comment = Comment(
                content=f'Test comment {i}',
                ticket=test_ticket,
                author=test_user
            )
            comments.append(comment)
            db.session.add(comment)
        db.session.commit()
        
        comment_ids = [c.id for c in comments]
        
        # Login and delete the ticket
        auth_client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123'
        })
        
        response = auth_client.post(f'/tickets/{test_ticket.id}/delete',
                                  follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Ticket deleted successfully' in response.data
        
        # Verify ticket and all comments are deleted
        assert Ticket.query.get(test_ticket.id) is None
        for comment_id in comment_ids:
            assert Comment.query.get(comment_id) is None

def test_ticket_delete_nonexistent(auth_client, test_user):
    """Test attempting to delete a non-existent ticket."""
    with auth_client:
        # Login
        auth_client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'password123'
        })
        
        # Try to delete non-existent ticket
        response = auth_client.post('/tickets/99999/delete',
                                  follow_redirects=True)
        
        assert response.status_code == 404 