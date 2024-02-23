# app/auth/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask import render_template, url_for, redirect, flash, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc
from datetime import datetime
import logging

from app.forms.auth_forms import EmailRegistrationForm, UserRegistrationForm, UserLoginForm, ResetPasswordForm, ForgotPasswordForm, ChangePasswordForm, AddTelegramForm
from app.models.user import User, MonitoredAd
from app.models.report import Report
from app.extensions import db
from app.utils.decorators import logout_required
from app.utils.token import get_token_for_email_registration, confirm_email_registration_token
from scripts.utils import convert_utc_to_ist, count_query_occurance, count_query_occurrence_selenium, get_webpage_sha256, get_webpage_sha256_selenium
from scripts.email_message import EmailMessage
from config import EmailConfig
from . import auth_bp

logger = logging.getLogger(__name__)

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
                logger.info(f"User '{user.email}' successfully logged in.")

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
                username=user.nickname
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
                logger.info(f"Password reset instructions sent to '{user.email}'.")
                return redirect(url_for('auth.login'))

            except Exception as e:
                # TODO: Handle email sending error better
                flash('An error occurred while attempting to send the password reset instructions. Try again!', 'danger')
                logger.error("An error occurred while attempting to send the password reset instructions")
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
        logger.info(f"Password reset successful for '{user.email}'.")
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
            
            # Send acc_registration_url to the new user form.email.data.
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
                logger.info(f"New acc registration instruction sent over email to '{form.email.data}'.")
                form = EmailRegistrationForm(formdata=None)
                return render_template('register_email.html', form=form)
            
            except Exception as e:
                # TODO: Handle email sending error better
                flash('An error occurred while attempting to send the account registration link through email. Try again!', 'danger')
                logger.error("Error occurred while attempting to send the account registration link through email.")
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

        if form.telegram.data:
            # Check whether there is any user with the same telegram number!
            telegram_user = User.query.filter_by(telegram=form.telegram.data).first()
        else:
            telegram_user = None

        if telegram_user is None:
            # Create the user
            user = User(
                fullname=user_data['fullname'],
                email = user_data['email'],
                nickname = form.nickname.data,
                telegram = form.telegram.data
            )

            # Set password for the user using the set_hashed_password method
            user.set_hashed_password(form.passwd.data)

            # Set nickname for the user using set_nickname method
            user.set_nickname()

            # Add the user to the database
            db.session.add(user)
            db.session.commit()

            flash("Congratulations! Your account has been successfully created. You can now log in using the provided credentials.", 'success')
            logger.info(f"New account created successfully for user '{user.email}'.")
            return redirect(url_for('auth.login'))

        else:
            # Telegram id taken
            flash("Telegram id is taken. Try different one!", 'warning')
    
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
    logger.info("User logged out successfully.")

    return redirect(url_for('auth.login'))


@auth_bp.route('/add_advertisement', methods=['POST'])
@login_required
def add_advertisement():
    try:
        # Get the data from the POST request
        title = request.form.get('title')
        advertisement_number = request.form.get('advertisement_number')
        website_url = request.form.get('website_url')
        description = request.form.get('description')

        # Calculate the count
        occurrence_count = count_query_occurance(url=website_url, query_str=advertisement_number)
        
        if occurrence_count > 0:
            # Everything is fine!

            ad_user_id = current_user.id

            monitored_ad = MonitoredAd(
                title=title,
                advertisement_number = advertisement_number,
                website_url = website_url,
                description=description,
                occurrence_count=occurrence_count,
                user_id = ad_user_id
            )

            # Set web page hash
            h = get_webpage_sha256(url=monitored_ad.website_url)
            if h != -1:
                # Hash found
                monitored_ad.page_content_hash = h
            else:
                flash(f"Cannot reach the webpage '{monitored_ad.website_url}' rightnow. Try again later!")
                return jsonify({'error': False}), 500
            
            monitored_ad.last_updated = datetime.utcnow()

            # Add the new advertisement to the database
            db.session.add(monitored_ad)
            db.session.commit()

            # Return a success response
            flash("Advertisement entry added successfully!", 'success')
            logger.info(f"User '{current_user.email}' added one entry to their dashboard.")
            return jsonify({'success': True}), 200
        
        elif occurrence_count == 0:
            # Adv num is not on the page.
            # Check with selenium
            occurrence_count = count_query_occurrence_selenium(url=website_url, query_str=advertisement_number)
            if occurrence_count > 0:
                # Add it
                ad_user_id = current_user.id

                monitored_ad = MonitoredAd(
                    title=title,
                    advertisement_number = advertisement_number,
                    website_url = website_url,
                    description=description,
                    occurrence_count=occurrence_count,
                    user_id = ad_user_id
                )

                # Set web page hash
                h = get_webpage_sha256_selenium(url=monitored_ad.website_url)
                if h != -1:
                    # Hash found
                    monitored_ad.page_content_hash = h
                else:
                    flash(f"Cannot reach the webpage '{monitored_ad.website_url}' rightnow. Try again later!")
                    return jsonify({'error': False}), 500

                monitored_ad.last_updated = datetime.utcnow()

                # Add the new advertisement to the database
                db.session.add(monitored_ad)
                db.session.commit()

                # Return a success response
                flash(f"Advertisement entry '{title}' added successfully!", 'success')
                logger.info(f"User '{current_user.email}' added one entry to their dashboard.")
                return jsonify({'success': True}), 200
                
            else:
                flash(f"The advertisement with the number '{advertisement_number}' is not present on the webpage. Please retry with a different advertisement number.", 'warning')
                return jsonify({'error': False}), 500
        
        else:
            # Error in the URL
            flash("An error occurred while trying to access the webpage. Please verify that the URL is valid.", 'error')
            return jsonify({'error': False}), 500
        
    except Exception as e:
        # Handle any errors that may occur during the process
        flash("Error. Looks like there was a problem to update the information into the database.", 'danger')
        logger.error(f"Database Error occured when user '{current_user.email}' tried to add entry to their dashboard.{e}")
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
                title = ad_to_delete.title
                db.session.delete(ad_to_delete)
                db.session.commit()

                flash(f"Advertisement '{title}' deleted successfully!", 'success')
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
    ad_title = request.json['advTitle']
    adv_num = request.json['advNum']
    adv_url = request.json['advUrl']
    adv_desc = request.json['advDesc']

    ad_to_update = MonitoredAd.query.get_or_404(ad_id)
    if ad_to_update.user_id == current_user.id:
        # Check the occurrence count
        occurrence_count = count_query_occurance(url=adv_url, query_str=adv_num)

        if occurrence_count > 0:
            # Everything fine!
            ad_to_update.title = ad_title
            ad_to_update.advertisement_number = adv_num
            ad_to_update.website_url = adv_url
            ad_to_update.description = adv_desc
            ad_to_update.occurrence_count = occurrence_count

            # Set web page hash
            h = get_webpage_sha256(url=ad_to_update.website_url)
            if h != -1:
                # Hash found
                ad_to_update.page_content_hash = h
            else:
                flash(f"Cannot reach the webpage '{ad_to_update.website_url}' rightnow. Try again later!")
                return jsonify({'error': False}), 500
            
            ad_to_update.last_updated = datetime.utcnow()

            try:
                db.session.commit()
                flash("The advertisement updated successfully.", 'success')
                logger.info(f"User entry updated by the user '{current_user.email}'.")
                return jsonify({'message': 'Advertisement updated successfully!'})

            except:
                flash("Error. Looks like there was a problem updating the information into the database.", 'danger')
                return jsonify({'error': 'Database error'})

        elif occurrence_count == 0:
            # Adv num is not on the page.
            flash(f"The advertisement with the number '{adv_num}' is not present on the webpage. Please retry with a different advertisement number.", 'warning')
            return jsonify({'error': 'Advertisement not found'})

        else:
            # Error in the URL
            flash("An error occurred while trying to access the webpage. Please verify that the URL is valid.", 'error')
            return jsonify({'error': 'URL error'})
    else:
        flash("You are not authorized to make that request.", 'warning')
        return jsonify({'error': 'Unauthorized'})


@auth_bp.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    form = ChangePasswordForm()
    
    user_to_update = User.query.get_or_404(user_id)

    if current_user.id == user_to_update.id:
        # Change the passwd
        if form.validate_on_submit():
            old_password = form.old_password.data
            new_password = form.new_password.data

            if user_to_update.check_password(old_password):
                # Change password
                user_to_update.set_hashed_password(new_password)

                # Commit the changes
                db.session.commit()

                flash("Password changed successfully.", 'success')
                logger.info(f"Password changed successfully for the user '{user_to_update.email}'.")
                return redirect(url_for('auth.dashboard'))

            else:
                # Password doesn't match
                flash("The old password you provided is incorrect. Please attempt it again.", 'error')
                return redirect(url_for('auth.dashboard', user_id=current_user.id))

    else:
        flash("Modifying passwords that belong to others is not allowed.", 'info')
        return redirect(url_for('auth.dashboard'))

    return render_template('change_password.html', form=form)

@auth_bp.route('/add_telegram/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_telegram(user_id):
    form = AddTelegramForm()

    user_to_update = User.query.get_or_404(user_id)

    if current_user.id == user_to_update.id:
        if user_to_update.telegram is not None:
            flash("Your Telegram user ID has already been included in our database.", 'info')
            return redirect(url_for('auth.dashboard'))
    
        # Change the telegram id
        if form.validate_on_submit():
            user_to_update.telegram = form.telegram_id.data

            # Commit
            db.session.commit()

            flash("Your telegram user id added successfully.", 'success')
            logger.info(f"Telegram id added for user '{user_to_update.email}.'")
            return redirect(url_for('auth.dashboard'))

    else:
        flash("Altering the Telegram user ID of others is not permitted.", 'info')
        return redirect(url_for('auth.dashboard'))

    return render_template('add_telegram.html', form=form)


@auth_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if request.method == 'POST':
        reporter_name = (
            None
            if request.form.get('reporter_name') == ''
            else request.form.get('reporter_name')
        )
        issue_description = request.form.get('issue_description')

        if issue_description:
            new_report = Report(reporter_name=reporter_name, issue_description=issue_description)
            db.session.add(new_report)
            db.session.commit()
            flash('Issue reported successfully!', 'success')
            logger.info(f"New report issued by `{reporter_name}`.")
            return redirect(url_for('auth.report'))

    # Fetch all reports for display
    reports = Report.query.order_by(desc(Report.created_at)).all()
    return render_template('report.html', reports=reports, convert_utc_to_ist=convert_utc_to_ist)


@auth_bp.route('/resolve_report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)

    if current_user.email == 'indrajitghosh912@gmail.com':
        report.status = True
        db.session.commit()
        flash('Issue marked as resolved!', 'success')
        logger.info("Issue resolved!")
    else:
        flash('You do not have permission to mark this issue as resolved.', 'danger')

    return redirect(url_for('auth.report'))