"""
Email utility functions for ARB Feedback Portal authentication.
"""

import datetime
from flask import current_app, render_template, url_for
from flask_mail import Message
from arb.auth import get_mail
from arb.auth.models import User

# ... (rest of the code is the same as before, just update imports) 

def send_welcome_email(user):
    """
    Send a welcome email to the newly registered user.
    """
    subject = "Welcome to ARB Feedback Portal"
    recipient = user.email
    html_body = render_template('emails/welcome.html', user=user)
    msg = Message(subject=subject, recipients=[recipient], html=html_body)
    get_mail().send(msg)


def send_password_reset_email(user, token):
    """
    Send a password reset email to the user with a reset token.
    """
    subject = "Password Reset Request"
    recipient = user.email
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    html_body = render_template('emails/password_reset.html', user=user, reset_url=reset_url)
    msg = Message(subject=subject, recipients=[recipient], html=html_body)
    get_mail().send(msg) 