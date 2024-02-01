# app/auth/__init__.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask import Blueprint

auth_bp = Blueprint(
    'auth', 
    __name__,
    template_folder="templates", 
    static_folder="static",
    url_prefix='/auth'
)

from app.auth import routes