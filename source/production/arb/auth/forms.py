"""
Authentication forms for ARB Feedback Portal.

This module defines all WTForms used for user authentication.
"""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from arb.auth.models import get_user_model

class RegistrationForm(FlaskForm):
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        User = get_user_model()
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email address is already registered. Please use a different email or try logging in.')

class LoginForm(FlaskForm):
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class PasswordResetForm(FlaskForm):
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.')
    ])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        User = get_user_model()
        user = User.query.filter_by(email=email.data.lower()).first()
        if not user:
            raise ValidationError('No account found with this email address.')

class ForgotUsernameForm(FlaskForm):
    submit = SubmitField('Get Username Recovery Help')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required.'),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password') 