# app/utils/decorators.py
# Author: Indrajit Ghosh
# Created On: Feb 04, 2024

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already registered.", "info")
            return redirect(url_for("auth.dashboard"))
        return func(*args, **kwargs)

    return decorated_function