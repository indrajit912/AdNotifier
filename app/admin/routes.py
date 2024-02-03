# app/admin/routes.py
# Author: Indrajit Ghosh
# Created On: Feb 02, 2024
#
from flask import render_template, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc

from app.models.user import User, MonitoredAd
from app.extensions import db
from scripts.utils import convert_utc_to_ist
from config import EmailConfig

from . import admin_bp

@admin_bp.route('/')
@login_required
def home():
    # TODO: Change the following condition to `if current_user.is_admin`
    if current_user.is_admin or current_user.email == EmailConfig.INDRAJIT912_GMAIL:
        # Retrieve all users and monitored ads from the database
        users = User.query.order_by(desc(User.created_at)).all()
        monitored_ads = MonitoredAd.query.order_by(desc(MonitoredAd.created_at)).all()

        return render_template(
            'admin.html', 
            users=users, 
            monitored_ads=monitored_ads, 
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
    # TODO: Change the following condition to `if current_user.is_admin`
    if current_user.is_admin or current_user.email == EmailConfig.INDRAJIT912_GMAIL:
        user_to_delete = User.query.get_or_404(id)
        
        if current_user.id == user_to_delete.id:
            flash("You cannot delete yourself!", 'warning')
            return redirect(url_for('admin.home'))
        else:
            try:
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

    # Update the database
    db.session.commit()

    flash(f'Admin status for user {user.fullname} has been updated.', 'success')
    return redirect(url_for('admin.home'))
