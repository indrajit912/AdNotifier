# app/extensions.py
# 
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

