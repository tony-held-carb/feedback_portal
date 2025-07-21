"""
Email utility functions for ARB Feedback Portal authentication.
"""

import logging

from flask import current_app, render_template, url_for
from flask_mail import Message

from arb.auth import get_mail

logger = logging.getLogger(__name__)


# ... (rest of the code is the same as before, just update imports)

def send_welcome_email(user):
  """
  Send a welcome email to the newly registered user.
  """
  subject = "Welcome to ARB Feedback Portal"
  recipient = user.email
  html_body = render_template('emails/welcome.html', user=user)
  msg = Message(subject=subject, recipients=[recipient], html=html_body)

  # Log email content if suppressed
  if current_app.config.get('MAIL_SUPPRESS_SEND', False):
    logger.info("=" * 60)
    logger.info("SUPPRESSED EMAIL - Welcome Email")
    logger.info("=" * 60)
    logger.info(f"To: {recipient}")
    logger.info(f"Subject: {subject}")
    logger.info("HTML Body:")
    logger.info(html_body)
    logger.info("=" * 60)

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

  # Log email content if suppressed
  if current_app.config.get('MAIL_SUPPRESS_SEND', False):
    logger.info("=" * 60)
    logger.info("SUPPRESSED EMAIL - Password Reset")
    logger.info("=" * 60)
    logger.info(f"To: {recipient}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Reset URL: {reset_url}")
    logger.info("HTML Body:")
    logger.info(html_body)
    logger.info("=" * 60)

  get_mail().send(msg)


def send_email_confirmation(user, token):
  """
  Send an email confirmation email to the user with a confirmation token.
  """
  subject = "Confirm Your Email Address - ARB Feedback Portal"
  recipient = user.email
  confirmation_url = url_for('auth.confirm_email', token=token, _external=True)
  html_body = render_template('emails/email_confirmation.html', user=user, confirmation_url=confirmation_url)
  msg = Message(subject=subject, recipients=[recipient], html=html_body)

  # Log email content if suppressed
  if current_app.config.get('MAIL_SUPPRESS_SEND', False):
    logger.info("=" * 60)
    logger.info("SUPPRESSED EMAIL - Email Confirmation")
    logger.info("=" * 60)
    logger.info(f"To: {recipient}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Confirmation URL: {confirmation_url}")
    logger.info("HTML Body:")
    logger.info(html_body)
    logger.info("=" * 60)

  get_mail().send(msg)
