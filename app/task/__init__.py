# app/task/__init__.py
# Author: Indrajit Ghosh
# Created On: Feb 03, 2024
#

from flask import Blueprint

task_bp = Blueprint(
    'task', 
    __name__,
    template_folder="templates", 
    static_folder="static",
    url_prefix='/task'
)

from app.task import routes