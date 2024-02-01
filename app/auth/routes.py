# app/auth/routes.py
from flask import render_template, url_for, redirect, flash
from app.auth.forms import UserSignupForm
from app.models.user import User
from app.extensions import db

from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic here
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # Signup logic here
    fullname = None
    form = UserSignupForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(
                fullname=form.fullname.data,
                email = form.email.data,
                whatsapp = form.whatsapp.data
            )

            # Set password for the user using the set_hashed_password method
            user.set_hashed_password(form.passwd.data)

            # Add the user to the database
            db.session.add(user)
            db.session.commit()
        
        fullname = form.fullname.data
        form.fullname.data = form.email.data = form.passwd.data = form.whatsapp.data = ''

        flash("User added successfully!", 'success')
    
    our_users = User.query.order_by(User.created_at)

    return render_template(
        'signup.html',
        fullname=fullname,
        form=form,
        our_users=our_users
    )