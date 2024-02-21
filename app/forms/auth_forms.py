# app/forms/auth_forms.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Optional, Length, Email, ValidationError

from app.models.user import User


class UserLoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class EmailRegistrationForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])

    submit = SubmitField("Next")


class UserRegistrationForm(FlaskForm):
    passwd = PasswordField(
        "Password", 
        validators=[DataRequired(), EqualTo('confirm_passwd', message='Passwords must match')]
    )
    confirm_passwd = PasswordField("Confirm password")
    nickname = StringField("Nickname", validators=[Optional()])
    telegram = IntegerField("Telegram User ID", validators=[Optional()])

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

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Old Password',
        validators=[DataRequired(message="To modify the password, the previous one must be provided.")]
    )
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
    submit = SubmitField('Submit')


class AddTelegramForm(FlaskForm):
    telegram_id = IntegerField("Enter Telegram User ID", validators=[DataRequired()])

    submit = SubmitField('Submit')

