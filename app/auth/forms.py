from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class UserSignupForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")