# app/auth/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask import render_template, url_for, redirect, flash, session, request
from flask_login import login_required, login_user, logout_user, current_user

from app.forms.auth_forms import UserSignupForm, UserSignupFormNext, AdvertisementForm, UserLoginForm
from app.models.user import User, MonitoredAd
from app.extensions import db
from scripts.utils import convert_utc_to_ist, generate_otp
from scripts.email_message import EmailMessage
from config import EmailConfig
from . import auth_bp


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
    user_ads = MonitoredAd.query.filter_by(user_id=current_user.id).order_by(MonitoredAd.last_updated).all()
    return render_template('dashboard.html', user=user, user_ads=user_ads, convert_utc_to_ist=convert_utc_to_ist)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", 'success')

    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form_step = int(request.form.get('step', session.get('step', 1)))

    if form_step == 1:
        form = UserSignupForm()
    elif form_step == 2:
        form = UserSignupFormNext()

    if form.validate_on_submit():
        if form_step == 1:
            # Check for a user with the given email id in the db
            exsting_user = User.query.filter_by(email=form.email.data).first()

            if exsting_user is None:
                # Process the first step, generate OTP, and send it to the email
                otp = generate_otp()

                # Email otp
                # Render the email template with the provided parameters
                _email_html_text = render_template(
                    'email_otp.html',
                    username=form.fullname.data,
                    otp=otp
                )

                # Create the email message
                msg = EmailMessage(
                    sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
                    to=form.email.data,
                    subject="AdNotifier: OTP for your registration!",
                    email_html_text=_email_html_text
                )

                # Send OTP via email
                try:
                    # Send the email to Indrajit
                    msg.send(
                        sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD, 
                        server_info=EmailConfig.GMAIL_SERVER,
                        print_success_status=False
                    )

                    # Store the form data in the session
                    session['otp'] = otp
                    session['fullname'] = form.fullname.data
                    session['email'] = form.email.data
                    session['step'] = 2

                    flash('OTP sent to your email. Please check and enter below.', 'info')
                    return redirect(url_for('auth.signup'))

                except:
                    # Handle email sending error
                    flash('An error occurred while attempting to send the OTP. Try again!', 'danger')
                    return redirect(url_for('auth.signup'))

                
            else:
                # User exists already
                flash("Email id taken. Try different one!", 'warning')
                return redirect(url_for('auth.signup'))
        
        elif form_step == 2:

            if form.otp.data == session['otp']:
                # OTP matched!
                if form.whatsapp.data:
                    # Check whether there is any user with the same whatsapp number!
                    whatsapp_user = User.query.filter_by(whatsapp=form.whatsapp.data).first()
                else:
                    whatsapp_user = None

                if whatsapp_user is None:
                    # Process the second step, complete registration, etc.
                    user = User(
                        fullname=session['fullname'],
                        email = session['email'],
                        whatsapp = form.whatsapp.data
                    )

                    # Set password for the user using the set_hashed_password method
                    user.set_hashed_password(form.passwd.data)

                    # Add the user to the database
                    db.session.add(user)
                    db.session.commit()

                    # Clear the session data
                    session.pop('fullname', None)
                    session.pop('email', None)
                    session.pop('step', None)

                    flash("Congratulations! Your account has been successfully created. You can now log in using the provided credentials.", 'success')
                    return redirect(url_for('auth.login'))

                else:
                    # Whatsapp number taken
                    flash("Whatsapp number is taken. Try different one!", 'warning')

                    # Clear the session data
                    session.pop('fullname', None)
                    session.pop('email', None)
                    session.pop('step', None)
                    session.pop('otp', None)

                    return redirect(url_for('auth.signup'))
            
            else:
                # Wrong otp
                flash("Wrong OTP. Please try again.", 'danger')

                # Clear the session data
                session.pop('fullname', None)
                session.pop('email', None)
                session.pop('step', None)
                session.pop('otp', None)

                return redirect(url_for('auth.signup'))

    return render_template('signup.html', form=form)


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
        return redirect(url_for('auth.dashboard'))
    
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