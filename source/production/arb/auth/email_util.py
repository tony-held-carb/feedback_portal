"""
Email utility functions for ARB Feedback Portal authentication.
"""

import datetime
from flask import current_app, render_template, url_for
from flask_mail import Message
from arb.portal.extensions import mail
from arb.auth.models import User

# ... (rest of the code is the same as before, just update imports) 