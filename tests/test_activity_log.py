import pytest
from datetime import datetime
from flask import url_for
from app.activity_log import ActivityLog, log_activity
from app.models import User
from app import db

def test_activity_log_creation(test_client, init_database):
    """Test creating an activity log entry."""
    # Create a test user
    user = User.query.filter_by(username='test_user').first()
    
    # Log an activity
    log_activity(
        activity_type='test_activity',
        description='Test activity description',
        resource_type='test',
        resource_id=1,
        additional_data={'test_key': 'test_value'},
        user=user,
        ip_address='127.0.0.1'
    )
    
    # Retrieve the log entry
    log_entry = ActivityLog.query.filter_by(activity_type='test_activity').first()
    
    # Verify the log entry
    assert log_entry is not None
    assert log_entry.user_id == user.id
    assert log_entry.activity_type == 'test_activity'
    assert log_entry.description == 'Test activity description'
    assert log_entry.resource_type == 'test'
    assert log_entry.resource_id == 1
    assert log_entry.ip_address == '127.0.0.1'
    assert log_entry.additional_data == {'test_key': 'test_value'}
    assert isinstance(log_entry.timestamp, datetime)

def test_activity_log_anonymous(test_client, init_database):
    """Test logging activity without a user."""
    # Log an activity without a user
    log_activity(
        activity_type='anonymous_activity',
        description='Anonymous activity',
        ip_address='127.0.0.1'
    )
    
    # Retrieve the log entry
    log_entry = ActivityLog.query.filter_by(activity_type='anonymous_activity').first()
    
    # Verify the log entry
    assert log_entry is not None
    assert log_entry.user_id is None
    assert log_entry.description == 'Anonymous activity'
    assert log_entry.ip_address == '127.0.0.1'

def test_activity_log_relationship(test_client, init_database):
    """Test the relationship between ActivityLog and User."""
    # Create a test user
    user = User.query.filter_by(username='test_user').first()
    
    # Create multiple log entries
    for i in range(3):
        log_activity(
            activity_type=f'test_activity_{i}',
            description=f'Test activity {i}',
            user=user
        )
    
    # Verify the user's activity logs
    assert user.activity_logs.count() == 3
    
    # Verify the logs are ordered by timestamp (newest first)
    logs = user.activity_logs.all()
    assert logs[0].activity_type == 'test_activity_2'
    assert logs[1].activity_type == 'test_activity_1'
    assert logs[2].activity_type == 'test_activity_0'

def test_activity_log_error_handling(test_client, init_database):
    """Test error handling in activity logging."""
    # Test with invalid JSON data
    class InvalidJSON:
        def __str__(self):
            return "Invalid JSON object"
    
    # This should not raise an exception, but log an error
    log_activity(
        activity_type='error_test',
        description='Error test',
        additional_data=InvalidJSON()
    )
    
    # Verify no log entry was created
    log_entry = ActivityLog.query.filter_by(activity_type='error_test').first()
    assert log_entry is None

def test_activity_log_cleanup(test_client, init_database):
    """Test cleaning up old activity logs."""
    # This would be implemented when we add log cleanup functionality
    pass 