from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from app.config import config
from app.logging_config import setup_logging
from app import security

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize logging
    setup_logging(app)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Initialize security features
    security.init_app(app)

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.tickets import bp as tickets_bp
    app.register_blueprint(tickets_bp)

    # Setup error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url if request else "No URL"}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f'Forbidden access attempt: {request.url if request else "No URL"}')
        return render_template('errors/403.html'), 403

# Import models to ensure they are registered with SQLAlchemy
from app import models 