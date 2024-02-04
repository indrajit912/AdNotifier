# app/forms/auth_forms.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Optional, Length


class UserLoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EmailRegistrationForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])

    submit = SubmitField("Next")


class UserRegistrationForm(FlaskForm):
    passwd = PasswordField(
        "Password", 
        validators=[DataRequired(), EqualTo('confirm_passwd', message='Passwords must match')]
    )
    confirm_passwd = PasswordField("Confirm password")
    nickname = StringField("Nickname", validators=[Optional()])
    whatsapp = IntegerField("WhatsApp", validators=[Optional()])

    submit = SubmitField("Register")


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message='Email is required.')
        ]
    )
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=6, message='Password must be at least 6 characters.'),
            EqualTo('confirm_password', message='Passwords must match.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(message='Please confirm your password.')]
    )
    submit = SubmitField('Reset')

