from flask import Blueprint, render_template, current_app, request, jsonify
from werkzeug.exceptions import HTTPException
from app import db
from .exceptions import InternalJiraError

bp = Blueprint('errors', __name__)

def wants_json_response():
    return request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html

@bp.app_errorhandler(404)
def not_found_error(error):
    current_app.logger.warning(
        f"404 Error accessing {request.url} - {error}",
        extra={'remote_addr': request.remote_addr}
    )
    if wants_json_response():
        return jsonify(error="Resource not found"), 404
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    current_app.logger.error(
        f"500 Internal Server Error: {error}",
        exc_info=True,
        extra={
            'remote_addr': request.remote_addr,
            'url': request.url,
            'method': request.method
        }
    )
    if wants_json_response():
        return jsonify(error="Internal server error"), 500
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    current_app.logger.warning(
        f"403 Forbidden access to {request.url} - {error}",
        extra={'remote_addr': request.remote_addr}
    )
    if wants_json_response():
        return jsonify(error="Forbidden"), 403
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(401)
def unauthorized_error(error):
    current_app.logger.warning(
        f"401 Unauthorized access to {request.url} - {error}",
        extra={'remote_addr': request.remote_addr}
    )
    if wants_json_response():
        return jsonify(error="Unauthorized"), 401
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(InternalJiraError)
def handle_internal_jira_error(error):
    """Handle custom Internal Jira exceptions."""
    response = jsonify(error=str(error.message))
    response.status_code = error.status_code
    current_app.logger.error(
        f"Internal Jira Error ({error.status_code}): {error.message}",
        exc_info=True,
        extra={
            'remote_addr': request.remote_addr,
            'url': request.url,
            'method': request.method
        }
    )
    if wants_json_response():
        return response
    return render_template(f'errors/{error.status_code}.html'), error.status_code

@bp.app_errorhandler(HTTPException)
def handle_http_exception(error):
    """Handle all other HTTP exceptions."""
    response = jsonify(error=str(error.description))
    response.status_code = error.code
    current_app.logger.error(
        f"HTTP Exception ({error.code}): {error.description}",
        exc_info=True,
        extra={
            'remote_addr': request.remote_addr,
            'url': request.url,
            'method': request.method
        }
    )
    if wants_json_response():
        return response
    return render_template(f'errors/{error.code}.html'), error.code 