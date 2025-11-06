"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class RegisterForm(FlaskForm):
    """User registration form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Validate that email is not already registered and verified."""
        email = field.data.strip().lower()
        
        # Check if email is already registered
        existing_user = User.find_by_email(email)
        if existing_user and existing_user.is_verified:
            raise ValidationError('Email is already registered and verified. Please login instead.')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class OTPVerifyForm(FlaskForm):
    """OTP verification form."""
    otp_code = StringField('OTP Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='OTP must be 6 digits')
    ])
    submit = SubmitField('Verify')

