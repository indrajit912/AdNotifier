# app/auth/routes.py
from flask import render_template, url_for, redirect
from app.auth.forms import UserSignupForm

from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic here
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Signup logic here
    name = None
    form = UserSignupForm()

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        

    return render_template(
        'signup.html',
        name=name,
        form=form
    )