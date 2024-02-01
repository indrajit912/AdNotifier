from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField
from wtforms.validators import DataRequired

class UserLoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserSignupForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    passwd = PasswordField("Choose a password", validators=[DataRequired()])
    # confirm_passwd = PasswordField("Confirm your password", validators=[DataRequired()])

    whatsapp = IntegerField("WhatsApp number")

    submit = SubmitField("Submit")


class AdvertisementForm(FlaskForm):
    advertisement_number = StringField("Advertisement Number", validators=[DataRequired()])
    website_url = StringField("Website URL", validators=[DataRequired()])

    submit = SubmitField("Submit")
