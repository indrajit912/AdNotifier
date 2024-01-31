# Flask Application - AdNotifier
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from flask import Flask
from .extensions import db, migrate

from config import ProductionConfig


def create_app(config_class=ProductionConfig):
    """
    Creates an app with specific config class
    """

    # Initialize the webapp
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # login_manager.init_app(app)

    # Register all blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)


    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application AdNotifier!</h1>'
    

    return app

