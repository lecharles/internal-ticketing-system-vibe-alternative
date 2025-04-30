"""Custom exceptions for the Internal Jira application."""

class InternalJiraError(Exception):
    """Base exception class for Internal Jira application."""
    def __init__(self, message=None, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or 500

class ValidationError(InternalJiraError):
    """Raised when input validation fails."""
    def __init__(self, message="Invalid input"):
        super().__init__(message, status_code=400)

class ResourceNotFoundError(InternalJiraError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type, resource_id):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message, status_code=404)

class AuthorizationError(InternalJiraError):
    """Raised when user doesn't have permission to perform an action."""
    def __init__(self, message="You don't have permission to perform this action"):
        super().__init__(message, status_code=403)

class AuthenticationError(InternalJiraError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication required"):
        super().__init__(message, status_code=401)

class DatabaseError(InternalJiraError):
    """Raised when a database operation fails."""
    def __init__(self, message="Database operation failed"):
        super().__init__(message, status_code=500) 