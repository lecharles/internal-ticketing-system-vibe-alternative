from flask import current_app
from flask_login import current_user
from datetime import datetime
from app import db
from app.models import ActivityLog

def log_activity(activity_type, description, resource_type=None, resource_id=None, additional_data=None, user=None, ip_address=None):
    """
    Log a user activity.
    
    Args:
        activity_type (str): Type of activity (e.g., 'login', 'create_ticket', 'delete_ticket')
        description (str): Human-readable description of the activity
        resource_type (str, optional): Type of resource being acted upon
        resource_id (int, optional): ID of the resource being acted upon
        additional_data (dict, optional): Any additional data to store
        user (User, optional): User performing the action (defaults to current_user)
        ip_address (str, optional): IP address of the user
    """
    try:
        # Get the current user if not provided
        if user is None and current_user and current_user.is_authenticated:
            user = current_user

        # Create activity log entry
        log_entry = ActivityLog(
            user_id=user.id if user else None,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            additional_data=additional_data
        )

        # Add and commit to database
        db.session.add(log_entry)
        db.session.commit()

        # Also log to application logger for system monitoring
        log_message = f"User {user.username if user else 'Anonymous'} - {activity_type}: {description}"
        if resource_type and resource_id:
            log_message += f" ({resource_type} #{resource_id})"
        
        current_app.logger.info(log_message)

    except Exception as e:
        current_app.logger.error(f"Failed to log activity: {str(e)}")
        # Don't re-raise the exception - logging should not break the main application flow 