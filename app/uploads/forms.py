"""Upload forms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class UploadForm(FlaskForm):
    """Content upload form."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters')
    ])
    image = FileField('Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    audio = FileField('Audio (Optional)', validators=[
        Optional(),
        FileAllowed(['mp3', 'wav', 'm4a', 'ogg'], 'Audio files only!')
    ])
    submit = SubmitField('Upload')

