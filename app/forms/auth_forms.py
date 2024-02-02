# app/forms/auth_forms.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Optional


class UserLoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserSignupForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])

    # New hidden field to store the step
    step = HiddenField(default="1")

    submit = SubmitField("Next")

class UserSignupFormNext(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired()])
    passwd = PasswordField(
        "Password", 
        validators=[DataRequired(), EqualTo('confirm_passwd', message='Passwords must match')]
    )
    confirm_passwd = PasswordField("Confirm password")
    whatsapp = IntegerField("WhatsApp", validators=[Optional()])

    # New hidden field to store the step
    step = HiddenField(default="2")

    submit = SubmitField("Register")


class AdvertisementForm(FlaskForm):
    advertisement_number = StringField("Advertisement Number", validators=[DataRequired()])
    website_url = StringField("Website URL", validators=[DataRequired()])

    submit = SubmitField("Submit")
