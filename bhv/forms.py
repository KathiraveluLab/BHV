from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class ImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[
        FileRequired(message='Please select an image'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=3, max=200, message='Title must be between 3 and 200 characters')
    ])
    
    description = TextAreaField('Description (Your Story)', validators=[
        Optional(),
        Length(max=5000, message='Description must be less than 5000 characters')
    ])
    
    submit = SubmitField('Upload Image')