# app/admin/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 02, 2024
#
from flask import render_template, url_for, redirect, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc
import logging

from app.models.user import User, MonitoredAd
from app.extensions import db, scheduler
from app.utils.decorators import admin_required
from scripts.utils import convert_utc_to_ist, get_lines_in_reverse
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
