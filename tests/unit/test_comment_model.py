import pytest
from datetime import datetime
from app.models import Comment, User, Ticket
from app import db

def test_create_comment(app, test_user, test_ticket):
    """Test comment creation."""
    with app.app_context():
        comment = Comment(
            content='Test comment content',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.id is not None
        assert comment.content == 'Test comment content'
        assert comment.ticket == test_ticket
        assert comment.author == test_user
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)
        
        # Clean up
        db.session.delete(comment)
        db.session.commit()

def test_comment_relationships(app, test_user, test_ticket):
    """Test comment relationships with User and Ticket."""
    with app.app_context():
        comment = Comment(
            content='Test relationships',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add(comment)
        db.session.commit()
        
        # Test User relationship
        assert comment in test_user.comments
        assert comment.author == test_user
        
        # Test Ticket relationship
        assert comment in test_ticket.comments
        assert comment.ticket == test_ticket
        
        # Clean up
        db.session.delete(comment)
        db.session.commit()

def test_comment_timestamps(app, test_user, test_ticket):
    """Test comment timestamp behavior."""
    with app.app_context():
        comment = Comment(
            content='Test timestamps',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add(comment)
        db.session.commit()
        
        creation_time = comment.created_at
        assert comment.updated_at == creation_time
        
        # Modify comment and check updated_at changes
        comment.content = 'Updated content'
        db.session.commit()
        
        assert comment.created_at == creation_time
        assert comment.updated_at > creation_time
        
        # Clean up
        db.session.delete(comment)
        db.session.commit()

def test_comment_cascade_delete(app, test_user, test_ticket):
    """Test cascade delete behavior."""
    with app.app_context():
        comment = Comment(
            content='Test cascade delete',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add(comment)
        db.session.commit()
        
        comment_id = comment.id
        
        # Delete ticket and verify comment is deleted
        db.session.delete(test_ticket)
        db.session.commit()
        
        # Verify comment was deleted
        assert Comment.query.get(comment_id) is None
        
        # Verify user still exists
        assert User.query.get(test_user.id) is not None

def test_comment_content_validation(app, test_user, test_ticket):
    """Test comment content validation."""
    with app.app_context():
        # Test empty content
        with pytest.raises(Exception):
            comment = Comment(
                content='',
                ticket=test_ticket,
                author=test_user
            )
            db.session.add(comment)
            db.session.commit()
        db.session.rollback()
        
        # Test None content
        with pytest.raises(Exception):
            comment = Comment(
                content=None,
                ticket=test_ticket,
                author=test_user
            )
            db.session.add(comment)
            db.session.commit()
        db.session.rollback()

def test_comment_representation(app, test_user, test_ticket):
    """Test string representation of comment."""
    with app.app_context():
        comment = Comment(
            content='Test repr',
            ticket=test_ticket,
            author=test_user
        )
        db.session.add(comment)
        db.session.commit()
        
        assert str(comment) == f'<Comment {comment.id} on Ticket {test_ticket.id}>'
        
        # Clean up
        db.session.delete(comment)
        db.session.commit()

def test_comment_author_required(app, test_ticket):
    """Test that comments require an author."""
    with app.app_context():
        with pytest.raises(Exception):
            comment = Comment(
                content='Test no author',
                ticket=test_ticket,
                author=None
            )
            db.session.add(comment)
            db.session.commit()
        db.session.rollback()

def test_comment_ticket_required(app, test_user):
    """Test that comments require a ticket."""
    with app.app_context():
        with pytest.raises(Exception):
            comment = Comment(
                content='Test no ticket',
                ticket=None,
                author=test_user
            )
            db.session.add(comment)
            db.session.commit()
        db.session.rollback()

def test_multiple_comments_per_ticket(app, test_user, test_ticket):
    """Test multiple comments on a single ticket."""
    with app.app_context():
        comments = []
        for i in range(3):
            comment = Comment(
                content=f'Comment {i}',
                ticket=test_ticket,
                author=test_user
            )
            comments.append(comment)
            db.session.add(comment)
        db.session.commit()
        
        # Verify all comments are associated with the ticket
        assert test_ticket.comments.count() == 3
        for i, comment in enumerate(test_ticket.comments):
            assert comment.content == f'Comment {i}'
        
        # Clean up
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()

def test_comment_ordering(app, test_user, test_ticket):
    """Test that comments are ordered by creation time."""
    with app.app_context():
        comments = []
        for i in range(3):
            comment = Comment(
                content=f'Comment {i}',
                ticket=test_ticket,
                author=test_user
            )
            comments.append(comment)
            db.session.add(comment)
            db.session.commit()  # Commit each comment to ensure different timestamps
        
        # Verify comments are returned in chronological order
        ticket_comments = test_ticket.comments.all()
        for i in range(len(ticket_comments) - 1):
            assert ticket_comments[i].created_at <= ticket_comments[i + 1].created_at
        
        # Clean up
        for comment in comments:
            db.session.delete(comment)
        db.session.commit() 