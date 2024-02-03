# app/forms/main_forms.py
# Author: Indrajit Ghosh
# Created On: Feb 03, 2024
#

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Optional

class ContactIndrajitForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    send = SubmitField("Send")