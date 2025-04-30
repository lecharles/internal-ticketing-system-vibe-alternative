import os
import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information when available."""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        
        return super().format(record)

def setup_logging(app):
    """Configure logging for the application."""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file handler for general logs
    file_handler = RotatingFileHandler(
        'logs/internal_jira.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    
    # Set up file handler for error logs
    error_file_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    
    # Create formatters
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    error_file_handler.setFormatter(formatter)
    
    # Set log level based on app configuration
    if app.debug:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)
    
    # Remove default handlers
    app.logger.handlers = []
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    
    # Set app logger level
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # First log message
    app.logger.info('Internal Jira startup') 