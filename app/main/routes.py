# app/main/routes.py
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from . import main_bp
import logging
from flask import flash, redirect, render_template, url_for
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, Unauthorized, Forbidden, \
    TooManyRequests
from app.forms.main_forms import ContactIndrajitForm
from scripts.email_message import EmailMessage
from config import EmailConfig

logger = logging.getLogger(__name__)

#######################################################
#                      Homepage
#######################################################
@main_bp.route('/')
def index():
    logger.info("Visited homepage.")
    return render_template("index.html")

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactIndrajitForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message_parts = form.message.data.split('\n')

        # Render the email template with the provided parameters
        email_html_text = render_template(
            'contact_email.html',
            name=name,
            subject=subject,
            message_parts=message_parts,
            email_id=email
        )

        # Create the email message
        msg = EmailMessage(
            sender_email_id=EmailConfig.INDRAJITS_BOT_EMAIL_ID,
            to=EmailConfig.INDRAJIT912_GMAIL,
            subject="Message from AdNotifier website!",
            email_html_text=email_html_text,
        )

        try:
            # Send the email to Indrajit
            msg.send(
                sender_email_password=EmailConfig.INDRAJITS_BOT_EMAIL_PASSWD,
                server_info=EmailConfig.GMAIL_SERVER,
                print_success_status=False
            )

            form = ContactIndrajitForm(formdata=None)

            flash("Your email has been successfully delivered to Indrajit, and he will respond to you shortly.", 'success')
            logger.info("Email sent to Indrajit by some user!")
            return redirect(url_for('main.contact'))

        except Exception as e:
            # Handle email sending error
            flash("Error occured during email!")
            logger.error("Error occured during email to Indrajit.")
            return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)


@main_bp.route('/error/<error_code>')
def simulate_error(error_code):
    # Convert the error code to an integer
    error_code = int(error_code)

    # Raise an exception with the desired status code
    if error_code == 404:
        raise NotFound("Simulated 404 error")
    elif error_code == 500:
        raise InternalServerError("Simulated 500 error")
    elif error_code == 400:
        raise BadRequest("Simulated 400 error")
    elif error_code == 401:
        raise Unauthorized("Simulated 401 error")
    elif error_code == 403:
        raise Forbidden("Simulated 403 error")
    elif error_code == 429:
        raise TooManyRequests("Simulated 429 error")
    else:
        # You might want to handle other error codes accordingly
        raise Exception(f"Simulated error with code {error_code}")