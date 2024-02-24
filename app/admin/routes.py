# app/admin/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 02, 2024
#
from flask import render_template, url_for, redirect, flash, current_app, request
from flask_login import login_required, current_user
from sqlalchemy import desc
import logging
from datetime import datetime

from app.models.user import User, MonitoredAd
from app.extensions import db, scheduler
from app.forms.admin_forms import EmailForm
from app.utils.decorators import admin_required, indrajit_only
from scripts.utils import convert_utc_to_ist, get_lines_in_reverse, count_query_occurrences_and_hash
from scripts.email_message import EmailMessage
from config import EmailConfig, LOG_FILE

from . import admin_bp

logger = logging.getLogger(__name__)

@admin_bp.route('/')
@login_required
def home():
    # Change the following condition to `if current_user.is_admin`
    if current_user.is_admin or current_user.email == EmailConfig.INDRAJIT912_GMAIL:
        # Retrieve all users and monitored ads from the database
        users = User.query.order_by(desc(User.created_at)).all()
        monitored_ads = MonitoredAd.query.order_by(desc(MonitoredAd.created_at)).all()
        adv_job = scheduler.get_job("check_adv_count_job")
        logger.info(f"Admin dashboard visited by the admin '{current_user.email}'.")

        return render_template(
            'admin.html', 
            users=users, 
            monitored_ads=monitored_ads, 
            adv_job = adv_job,
            convert_utc_to_ist=convert_utc_to_ist,
            indrajit=EmailConfig.INDRAJIT912_GMAIL
        )
    else:
        flash("Only admin can visit this page!")
        return redirect(url_for('auth.dashboard'))
    

@admin_bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    # Check whether current user is an admin
    # Change the following condition to `if current_user.is_admin`
    if current_user.is_admin or current_user.email == EmailConfig.INDRAJIT912_GMAIL:
        user_to_delete = User.query.get_or_404(id)
        if user_to_delete.email == EmailConfig.INDRAJIT912_GMAIL:
            flash("You don't have the right to do so!", 'warning')
            return redirect(url_for('admin.home'))
        
        if current_user.id == user_to_delete.id:
            flash("You cannot delete yourself!", 'warning')
            return redirect(url_for('admin.home'))
        else:
            try:
                logger.info(f"User '{user_to_delete.email} is deleted by admin '{current_user.fullname}'.")
                db.session.delete(user_to_delete)
                db.session.commit()

                flash("User deleted successfully!", 'success')
                return redirect(url_for('admin.home'))
            except:
                flash("Opps! There was a problem deleting user. Try again.", 'danger')
    else:
        flash("Only admin can visit this page!", 'danger')
        return redirect(url_for('auth.dashboard'))
    
# Route to toggle the is_admin value
@admin_bp.route('/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    # Ensure the current user has admin privileges
    if not current_user.email == EmailConfig.INDRAJIT912_GMAIL:
        flash('You do not have permission to perform this action.', 'danger')
        logger.warning(f"The user '{current_user.email}' tried to toggle admin status!")
        return redirect(url_for('auth.dashboard'))

    # Get the user by ID
    user = User.query.get_or_404(user_id)

    # Toggle the is_admin value
    user.is_admin = not user.is_admin

    # Determine the current admin status
    current_admin_status = "enabled" if user.is_admin else "disabled"

    # Update the database
    db.session.commit()

    # Send an email to that user
    # Render the email template with the provided parameters
    _email_html_text = render_template(
        'admin_status.html',
        username=user.fullname,
        admin_status=current_admin_status
    )

    # Set subject based on admin_status
    subject = f"AdNotifier: Your admin status {'Enabled' if user.is_admin else 'Disabled'}"

    # Create the email message
    msg = EmailMessage(
        sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
        to=user.email,
        subject=subject,
        email_html_text=_email_html_text
    )

    try:
        # Send the email to Indrajit
        msg.send(
            sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD, 
            server_info=EmailConfig.GMAIL_SERVER,
            print_success_status=False
        )

        flash(f'Admin status for user {user.fullname} has been updated.', 'success')
        logger.info(f"Admin status for user '{user.fullname}' has been updated.")
        return redirect(url_for('admin.home'))

    except:
        # TODO: Handle email sending error better!
        flash('An error occurred while attempting to send the email!', 'danger')
        return redirect(url_for('admin.home'))
    

@admin_bp.route('/update_user_ad/<int:ad_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_user_ad(ad_id):
    ad_to_update = MonitoredAd.query.get_or_404(ad_id)

    occurrence_count, page_hash = count_query_occurrences_and_hash(url=ad_to_update.website_url, query_str=ad_to_update.advertisement_number)

    if occurrence_count > 0:
        # Everything fine!
        ad_to_update.occurrence_count = occurrence_count
        ad_to_update.page_content_hash = page_hash
        ad_to_update.last_updated = datetime.utcnow()

        try:
            db.session.commit()
            flash("User advertisement updated successfully.", 'success')
            logger.info(f"User entry updated by the admin '{current_user.email}'.")
            return redirect(url_for('admin.home'))
        
        except:
            flash("Error. Looks like there was a problem updating the information into the database.", 'danger')
            return redirect(url_for('admin.home'))
    else:
        flash(f"Error occurred during the update!")
        logger.error(f"Error occurred while updating the adv with id `{ad_id}`")
        return redirect(url_for('admin.home'))
    
@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    try:
        # Get the content of the log file
        logs = get_lines_in_reverse(LOG_FILE)
        
        return render_template('logs.html', logs=logs)
    except Exception as e:
        # Handle any exceptions that may occur during file reading
        current_app.logger.error(f"Error reading log file: {e}")
        return render_template('log_error.html', error_message="Error reading log file")


@admin_bp.route('/send_email', methods=['GET', 'POST'])
@login_required
@indrajit_only
def send_email():
    # Create an instance of the EmailForm
    form = EmailForm()
    users = User.query.all()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Get the subject, recipients, and body from the form
        subject = form.subject.data
        recipients = [e.strip() for e in form.recipients.data.split(',')]  # Assuming multiple recipients are comma-separated
        body_parts = form.body.data.split('\n')

        # Render the email template with the provided parameters
        email_html_text = render_template(
            'email_templates/user_email.html',
            body_parts=body_parts
        )

        # Create the email message
        msg = EmailMessage(
            sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
            to=recipients,
            subject=subject,
            email_html_text=email_html_text,
        )

        try:
            # Send the email to Indrajit
            msg.send(
                sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD,
                server_info=EmailConfig.GMAIL_SERVER,
                print_success_status=False
            )

            form = EmailForm(formdata=None)
        

            flash(f"Hey {current_user.nickname}! Your email has been sent succesfully to user(s).", 'success')
            logger.info(f"Email sent to user(s) by `{current_user.nickname}`!")
            return redirect(url_for('admin.home'))

        except Exception as e:
            # Handle email sending error
            flash("Error occured during email!")
            logger.error("Error occured during email to Indrajit.")
            return redirect(url_for('main.contact'))

        

    return render_template('send_email.html', form=form, users=users)