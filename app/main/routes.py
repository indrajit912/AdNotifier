# app/main/routes.py
#
# Author: Indrajit Ghosh
# Created On: Jan 31, 2024
#

from . import main_bp
from flask import flash, redirect, render_template, url_for
from app.forms.main_forms import ContactIndrajitForm
from scripts.email_message import EmailMessage
from config import EmailConfig

#######################################################
#                      Homepage
#######################################################
@main_bp.route('/')
def index():
    return render_template("index.html")


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactIndrajitForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        msg = form.message.data

        # Render the email template with the provided parameters
        email_html_text = render_template(
            'contact_email.html',
            name=name,
            subject=subject,
            msg=msg,
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
            return redirect(url_for('main.contact'))

        except Exception as e:
            # Handle email sending error
            flash("Error occured during email!")
            return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form)
