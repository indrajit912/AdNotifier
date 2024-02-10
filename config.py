# config.py
#
# Author: Indrajit Ghosh
# Created on: Jan 31, 2024
#
"""
Flask App Configuration

This module defines configuration settings for the Flask web application.

"""
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path
from secrets import token_hex

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).parent.resolve()

DB_HOST = os.environ.get("DB_HOST")

INDRA_ADNOTIFIER_TELEGRAM_BOT_TOKEN = os.environ.get("INDRA_ADNOTIFIER_TELEGRAM_BOT_TOKEN")

FLASK_ENV = os.environ.get("FLASK_ENV")

LOG_FILE = BASE_DIR / "app.log"

class EmailConfig:
    INDRAJITS_BOT_EMAIL_ID = os.environ.get("INDRAJITS_BOT_EMAIL_ID")
    INDRAJITS_BOT_EMAIL_PASSWD = os.environ.get("INDRAJITS_BOT_APP_PASSWORD")
    INDRAJIT912_GMAIL = os.environ.get("INDRAJIT912_GMAIL")
    GMAIL_SERVER = ['smtp.gmail.com', 587]

class DatabaseConfig:
    # Below are the PlanetScale db credentials
    DB_HOST = os.environ.get("DB_HOST")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")
    INDRAJIT_CLEVER_CLOUD_MYSQL_URI = os.environ.get("INDRAJIT_CLEVER_CLOUD_MYSQL_URI")

    # Database URI
    # Check if any of the required credentials is None
    if '' in (DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME):
        could_db_connection_uri = INDRAJIT_CLEVER_CLOUD_MYSQL_URI
    else:
        # Construct the Planet Scale Database URI
        could_db_connection_uri = (
            f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
            "?ssl_ca=/etc/ssl/cert.pem"
        )


class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or token_hex(16)
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or token_hex(16)

    SQLALCHEMY_DATABASE_URI = DatabaseConfig.could_db_connection_uri \
        or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or token_hex(16)
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or token_hex(16)

    SQLALCHEMY_DATABASE_URI = DatabaseConfig.could_db_connection_uri \
        or 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False