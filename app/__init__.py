# Flask Application - AdNotifier
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from flask import Flask

from config import ProductionConfig


def create_app(config_class=ProductionConfig):
    """
    Creates an app with specific config class
    """

    # Initialize the webapp
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize the app with db

    # Initialize the app and db with Flask-Migrate

    # Register all blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)


    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application AdNotifier!</h1>'
    

    return app

