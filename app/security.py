from functools import wraps
from flask import current_app, request, redirect, url_for

def check_https():
    """Check if the request is secure."""
    if not current_app.debug and not current_app.testing:
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

def add_security_headers(response):
    """Add security headers to the response."""
    if not hasattr(current_app, 'config'):
        return response
        
    headers = current_app.config.get('SECURE_HEADERS', {})
    for header, value in headers.items():
        if header not in response.headers:
            response.headers[header] = value
            
    return response

def ssl_required(func):
    """Decorator to require HTTPS."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_app.debug and not current_app.testing:
            if request.is_secure:
                return func(*args, **kwargs)
            else:
                return redirect(url_for(request.endpoint, 
                                      _external=True, 
                                      _scheme='https', 
                                      **request.view_args))
        return func(*args, **kwargs)
    return decorated_view

def init_app(app):
    """Initialize security features."""
    # Register HTTPS redirect middleware
    app.before_request(check_https)
    
    # Register security headers middleware
    app.after_request(add_security_headers)
    
    # Enable HSTS if not in debug/testing mode
    if not app.debug and not app.testing:
        app.config['SECURE_HEADERS']['Strict-Transport-Security'] = \
            'max-age=31536000; includeSubDomains' 