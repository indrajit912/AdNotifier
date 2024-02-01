# app/auth/routes.py
from flask import render_template, url_for, redirect, flash
from app.auth.forms import UserSignupForm, AdvertisementForm, UserLoginForm
from app.models.user import User, MonitoredAd
from app.extensions import db
from flask_login import login_required, login_user, logout_user, current_user

from . import auth_bp
from scripts.utils import convert_utc_to_ist


# Login view (route)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    # Login logic here
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Check the hash
            if user.check_password(form.passwd.data):
                # Password matched!
                login_user(user)
                flash("Login successful!", 'success')

                return redirect(url_for('auth.dashboard'))
            else:
                flash("Wrong passsword. Try again!")
        else:
            flash("That user doesn't exist! Try again...")
        
        form = UserLoginForm(formdata=None)


    return render_template('login.html', form=form)

@auth_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user
    user_ads = MonitoredAd.query.filter_by(user_id=current_user.id).order_by(MonitoredAd.created_at).all()
    return render_template('dashboard.html', user=user, user_ads=user_ads, convert_utc_to_ist=convert_utc_to_ist)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", 'success')

    return redirect(url_for('auth.login'))

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
        form = UserSignupForm(formdata=None)

        flash("Congratulations! Your account has been successfully created. You can now log in using the provided credentials.", 'success')
        return redirect(url_for('auth.login'))
    
    our_users = User.query.order_by(User.created_at)

    return render_template(
        'signup.html',
        fullname=fullname,
        form=form,
        our_users=our_users
    )


@auth_bp.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()

        flash("User deleted successfully!", 'success')
        return redirect(url_for('auth.signup'))
    except:
        flash("Opps! There was a problem deleting user. Try again.", 'danger')
        return redirect(url_for('main.index'))


@auth_bp.route('/add_advertisement', methods=['GET', 'POST'])
@login_required
def add_advertisement():
    form = AdvertisementForm()

    if form.validate_on_submit():
        ad_user_id = current_user.id

        monitored_ad = MonitoredAd(
            advertisement_number = form.advertisement_number.data,
            website_url = form.website_url.data,
            user_id = ad_user_id
        )

        # Clear the form
        form = AdvertisementForm(formdata=None)

        # Add the advertisement to the database
        db.session.add(monitored_ad)
        db.session.commit()

        flash("Advertisement entry added successfully!", 'success')
    
    ads = MonitoredAd.query.order_by(MonitoredAd.created_at)

    return render_template('add_advertisement.html', form=form, ads=ads)


@auth_bp.route('/delete_ad/<int:id>')
def delete_ad(id):
    ad_to_delete = MonitoredAd.query.get_or_404(id)

    try:
        db.session.delete(ad_to_delete)
        db.session.commit()

        flash("Advertisement deleted successfully!", 'success')
        return redirect(url_for('auth.add_advertisement'))
    except:
        flash("Opps! There was a problem deleting user. Try again.", 'danger')
        return redirect(url_for('main.index'))