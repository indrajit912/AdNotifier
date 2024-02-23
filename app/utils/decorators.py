# app/utils/decorators.py
# Author: Indrajit Ghosh
# Created On: Feb 04, 2024

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

INDRAJIT912 = 'indrajitghosh912@gmail.com'


def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already registered.", "info")
            return redirect(url_for("auth.dashboard"))
        return func(*args, **kwargs)

    return decorated_function

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            flash("Access restricted. Your account lacks the necessary permissions.", "info")
            return redirect(url_for("auth.dashboard"))
        return func(*args, **kwargs)

    return decorated_function

def indrajit_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.email != INDRAJIT912:
            flash("Access restricted. Your account lacks the necessary permissions.", "info")
            return redirect(url_for("auth.dashboard"))
        return func(*args, **kwargs)

    return decorated_function