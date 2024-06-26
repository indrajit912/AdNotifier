# Flask Application - AdNotifier
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

import logging
from flask import Flask
from .extensions import db, migrate, login_manager, scheduler

from config import ProductionConfig, LOG_FILE

def configure_logging(app: Flask):
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        filename=str(LOG_FILE)
    )
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    if app.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
        # Fix werkzeug handler in debug mode
        logging.getLogger('werkzeug').handlers = []


def create_app(config_class=ProductionConfig):
    """
    Creates an app with specific config class
    """

    # Initialize the webapp
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(app)

    # Register error handlers
    from app.error_handlers import page_not_found, internal_server_error, too_many_requests, \
        bad_request, forbidden, unauthorized
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(429, too_many_requests)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    scheduler.init_app(app)

    from . import tasks
    scheduler.start()

    from . import events

    # Register all blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.task import task_bp
    app.register_blueprint(task_bp)


    # Define the user loader function
    @login_manager.user_loader
    def load_user(user_id):
        # Replace this with the actual code to load a user from the database
        from app.models.user import User  # Import your User model
        return User.query.get(int(user_id))
    
    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application AdNotifier!</h1>'
    

    return app

