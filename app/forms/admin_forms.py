from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Optional, Length, Email, ValidationError

class EmailForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    recipients = StringField('Recipients (comma-separated)', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])