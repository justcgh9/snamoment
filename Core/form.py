"""Module for Flask-WTF custom forms"""

from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms.validators import DataRequired


class EditJSONForm(FlaskForm):
    """JSON editor form with hidden content field for linking Quill.js and Flask"""
    content = HiddenField('content', validators=[DataRequired()])
