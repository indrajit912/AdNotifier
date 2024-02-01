# app/main/routes.py
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from . import main_bp

from flask import render_template

#######################################################
#                      Homepage
#######################################################
@main_bp.route('/')
def index():
    return render_template("index.html")
