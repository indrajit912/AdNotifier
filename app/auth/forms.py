from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Optional

class UserLoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserSignupForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField(
        "Choose a password", 
        validators=[DataRequired(), EqualTo('confirm_passwd', message='Passwords must match')]
    )
    confirm_passwd = PasswordField("Confirm your password")
    whatsapp = IntegerField("WhatsApp number", validators=[Optional()])

    submit = SubmitField("Register")


class AdvertisementForm(FlaskForm):
    advertisement_number = StringField("Advertisement Number", validators=[DataRequired()])
    website_url = StringField("Website URL", validators=[DataRequired()])

    submit = SubmitField("Submit")
