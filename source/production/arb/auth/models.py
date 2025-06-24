"""
User model and authentication logic for ARB Feedback Portal.

This module defines the User class and all related authentication methods.
"""

import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.sql import func
from arb.portal.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active_col = Column('is_active', Boolean, default=True, nullable=False)
    is_confirmed_col = Column('is_confirmed', Boolean, default=False, nullable=False)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_timestamp = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True, unique=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    email_confirmation_token = Column(String(255), nullable=True, unique=True)
    email_confirmation_expires = Column(DateTime(timezone=True), nullable=True)
    role = Column(String(32), default='user', nullable=False)

    @property
    def is_active(self) -> bool:
        return bool(self.is_active_col)

    @property
    def is_confirmed(self) -> bool:
        return bool(self.is_confirmed_col)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(str(getattr(self, 'password_hash', '')), password)

    def is_account_locked(self) -> bool:
        account_locked_until = getattr(self, 'account_locked_until', None)
        if account_locked_until and account_locked_until > datetime.datetime.utcnow():
            return True
        elif account_locked_until is not None and account_locked_until <= datetime.datetime.utcnow():
            self.account_locked_until = None
            self.failed_login_attempts = 0
            db.session.commit()
        return False

    def record_failed_login(self, max_attempts: int = 5, lockout_duration: int = 900) -> None:
        failed_login_attempts = getattr(self, 'failed_login_attempts', 0) or 0
        failed_login_attempts = int(failed_login_attempts) + 1
        self.failed_login_attempts = failed_login_attempts
        if failed_login_attempts >= max_attempts:
            self.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=lockout_duration)
        db.session.commit()

    def record_successful_login(self) -> None:
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login_timestamp = datetime.datetime.utcnow()
        db.session.commit()

    def generate_password_reset_token(self, expiration_hours: int = 1) -> str:
        import secrets
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
        db.session.commit()
        return token

    def verify_password_reset_token(self, token: str) -> bool:
        password_reset_token = getattr(self, 'password_reset_token', None)
        password_reset_expires = getattr(self, 'password_reset_expires', None)
        if (password_reset_token == token and 
            password_reset_expires and 
            password_reset_expires > datetime.datetime.utcnow()):
            self.password_reset_token = None
            self.password_reset_expires = None
            db.session.commit()
            return True
        return False

    def generate_email_confirmation_token(self, expiration_hours: int = 24) -> str:
        import secrets
        token = secrets.token_urlsafe(32)
        self.email_confirmation_token = token
        self.email_confirmation_expires = datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours)
        db.session.commit()
        return token

    def verify_email_confirmation_token(self, token: str) -> bool:
        email_confirmation_token = getattr(self, 'email_confirmation_token', None)
        email_confirmation_expires = getattr(self, 'email_confirmation_expires', None)
        if (email_confirmation_token == token and 
            email_confirmation_expires and 
            email_confirmation_expires > datetime.datetime.utcnow()):
            self.is_confirmed_col = True
            self.email_confirmation_token = None
            self.email_confirmation_expires = None
            db.session.commit()
            return True
        return False

    def is_admin(self) -> bool:
        return str(getattr(self, 'role', '')) == 'admin'

    def has_role(self, role_name: str) -> bool:
        return str(getattr(self, 'role', '')) == role_name

    def __repr__(self) -> str:
        return f'<User: {self.id}, Email: {self.email}, Role: {self.role}, Active: {self.is_active}, Confirmed: {self.is_confirmed}>' 