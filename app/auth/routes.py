# app/auth/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask import render_template, url_for, redirect, flash, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc
from datetime import datetime

from app.forms.auth_forms import EmailRegistrationForm, UserRegistrationForm, UserLoginForm, ResetPasswordForm, ForgotPasswordForm
from app.models.user import User, MonitoredAd
from app.extensions import db
from app.utils.decorators import logout_required
from app.utils.token import get_token_for_email_registration, confirm_email_registration_token
from scripts.utils import convert_utc_to_ist
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
                flash("Wrong passsword. Try again!", 'error')
        else:
            flash("That user doesn't exist! Try again...", 'error')
        
        form = UserLoginForm(formdata=None)


    return render_template('login.html', form=form)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        # Check if the email exists in the database
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:

            # Generate a password reset token and send it via email
            reset_token = user.get_reset_password_token()
            reset_url = url_for('auth.reset_password', token=reset_token, _external=True)

            # Email reset URL to the user
            _email_html_text = render_template(
                'emails/email_reset_password.html',
                reset_url=reset_url,
                username=user.fullname
            )

            msg = EmailMessage(
                sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
                to=user.email,
                subject="AdNotifier: Password Reset Request",
                email_html_text=_email_html_text
            )

            try:
                msg.send(
                    sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD,
                    server_info=EmailConfig.GMAIL_SERVER,
                    print_success_status=False
                )

                flash('Password reset instructions sent to your email. Please check and follow the link.', 'info')
                return redirect(url_for('auth.login'))

            except Exception as e:
                # TODO: Handle email sending error better
                flash('An error occurred while attempting to send the password reset instructions. Try again!', 'danger')
                return redirect(url_for('auth.forgot_password'))

        else:
            flash("That email doesn't exist! Try again...", 'warning')

    return render_template('forgot_password.html', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)

    if not user:
        flash('Invalid or expired reset token. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        # Set the password for the user
        user.set_hashed_password(form.new_password.data)

        # Commit the changes
        db.session.commit()

        flash('Password reset successfully! You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', form=form)


@auth_bp.route('/register_email', methods=['GET', 'POST'])
@logout_required
def register_email():
    form = EmailRegistrationForm()

    if form.validate_on_submit():
        # Check whether the email already exists in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Email id taken. Try different one!", 'warning')
            return redirect(url_for('auth.register_email'))
        else:
            # Get the token
            token = get_token_for_email_registration(fullname=form.fullname.data, email=form.email.data)
            acc_registration_url = url_for('auth.register_user', token=token, _external=True)
            
            # TODO: Send acc_registration_url to the new user form.email.data.
            _email_html_text = render_template(
                'emails/email_register.html',
                acc_registration_url=acc_registration_url,
                username=form.fullname.data
            )

            msg = EmailMessage(
                sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
                to=form.email.data,
                subject="AdNotifier: New Account Registration",
                email_html_text=_email_html_text
            )

            try:
                msg.send(
                    sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD,
                    server_info=EmailConfig.GMAIL_SERVER,
                    print_success_status=False
                )

                flash('Almost there! New account registration instructions sent to your email. Please check and follow the link.', 'info')
                form = EmailRegistrationForm(formdata=None)
                return render_template('register_email.html', form=form)
            
            except Exception as e:
                # TODO: Handle email sending error better
                flash('An error occurred while attempting to send the account registration link through email. Try again!', 'danger')
                return redirect(url_for('auth.register_email'))


    return render_template('register_email.html', form=form)


@auth_bp.route('/register_user/<token>', methods=['GET', 'POST'])
def register_user(token):
    user_data = confirm_email_registration_token(token)

    if not user_data:
        flash('Invalid or expired reset token. Please try again.', 'danger')
        return redirect(url_for('auth.register_email'))
    
    form = UserRegistrationForm()

    if form.validate_on_submit():

        if form.whatsapp.data:
            # Check whether there is any user with the same whatsapp number!
            whatsapp_user = User.query.filter_by(whatsapp=form.whatsapp.data).first()
        else:
            whatsapp_user = None

        if whatsapp_user is None:
            # Create the user
            user = User(
                fullname=user_data['fullname'],
                email = user_data['email'],
                whatsapp = form.whatsapp.data
            )

            # Set password for the user using the set_hashed_password method
            user.set_hashed_password(form.passwd.data)

            # Add the user to the database
            db.session.add(user)
            db.session.commit()

            flash("Congratulations! Your account has been successfully created. You can now log in using the provided credentials.", 'success')
            return redirect(url_for('auth.login'))

        else:
            # Whatsapp number taken
            flash("Whatsapp number is taken. Try different one!", 'warning')
    
    return render_template('register_user.html', form=form, user_data=user_data)


@auth_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user
    user_ads = MonitoredAd.query.filter_by(user_id=current_user.id).order_by(desc(MonitoredAd.last_updated)).all()
    return render_template('dashboard.html', user=user, user_ads=user_ads, convert_utc_to_ist=convert_utc_to_ist)

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", 'success')

    return redirect(url_for('auth.login'))


@auth_bp.route('/add_advertisement', methods=['POST'])
@login_required
def add_advertisement():
    try:
        # Get the data from the POST request
        advertisement_number = request.form.get('advertisement_number')
        website_url = request.form.get('website_url')

        ad_user_id = current_user.id

        monitored_ad = MonitoredAd(
            advertisement_number = advertisement_number,
            website_url = website_url,
            user_id = ad_user_id
        )

        # Add the new advertisement to the database
        db.session.add(monitored_ad)
        db.session.commit()

        # Return a success response
        flash("Advertisement entry added successfully!", 'success')
        return jsonify({'success': True}), 200

    except Exception as e:
        # Handle any errors that may occur during the process
        flash("Error. Looks like there was a problem to update the information into the database.", 'danger')
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/delete_ad/<int:id>')
@login_required
def delete_ad(id):
    ad_to_delete = MonitoredAd.query.get_or_404(id)
    
    if ad_to_delete is not None:
        # proceed
        if ad_to_delete.user_id == current_user.id:
            # Delete the ad
            try:
                db.session.delete(ad_to_delete)
                db.session.commit()

                flash("Advertisement deleted successfully!", 'success')
                return redirect(url_for('auth.dashboard'))
            
            except:
                flash("Opps! There was a problem deleting user. Try again.", 'danger')
                return redirect(url_for('auth.dashboard'))
        else:
            flash("You don't have the permission to access this page!", 'info')
            return redirect(url_for('auth.dashboard'))
    else:
        # No add found
        flash("No advertisement found!", 'warning')
        return redirect(url_for('auth.dashboard'))


@auth_bp.route('/update_advertisement', methods=['POST'])
@login_required
def update_advertisement():
    ad_id = int(request.json['adId'])
    adv_num = request.json['advNum']
    adv_url = request.json['advUrl']

    ad_to_update = MonitoredAd.query.get_or_404(ad_id)
    if ad_to_update.user_id == current_user.id:
        ad_to_update.advertisement_number = adv_num
        ad_to_update.website_url = adv_url
        ad_to_update.last_updated = datetime.utcnow()

        try:
            db.session.commit()
            flash("The advertisement updated succesfully.", 'success')
            # Return a JSON response indicating success
            return jsonify({'message': 'Advertisement updated successfully!'})

        except:
            flash("Error. Looks like there was a problem to update the information into the database.", 'danger')
            return redirect(url_for('auth.dashboard'))
    else:
        flash("You are not authorized to do that request.", 'warning')
        return redirect(url_for('auth.dashboard'))
