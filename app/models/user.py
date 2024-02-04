# app/models/user.py
# Author: Indrajit Ghosh
# Created On: Feb 01, 2024
#

from datetime import datetime
import secrets
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_login import UserMixin

from app.extensions import db
from scripts.utils import sha256_hash


class MonitoredAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_number = db.Column(db.String(100), nullable=False)
    website_url = db.Column(db.String(255), nullable=False)
    occurrence_count = db.Column(db.Integer, default=0)  # New field to store the count
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # You can add additional fields as needed, e.g., last_checked_at, notification_status, etc.

    # Foreign Key to refer to the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    password_salt = db.Column(db.String(32), nullable=False)
    whatsapp = db.Column(db.Integer, default=None)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # User can have many MonitoredAd
    monitored_ads = db.relationship('MonitoredAd', backref='user', cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"User(id={self.id}, fullname={self.fullname}, email={self.email}, whatsapp={self.whatsapp}, is_admin={self.is_admin}, created_at={self.created_at}, last_updated={self.last_updated})"

    def set_hashed_password(self, password):
        """Sets the password_hash"""
        # Generate a random salt
        salt = secrets.token_hex(16)
        self.password_salt = salt

        # Combine password and salt, then hash
        password_with_salt = password + salt
        hashed_password = sha256_hash(password_with_salt)
        self.password_hash = hashed_password

    def check_password(self, password):
        # Combine entered password and stored salt, then hash and compare with stored hash
        password_with_salt = password + self.password_salt
        hashed_password = sha256_hash(password_with_salt)
        return hashed_password == self.password_hash
    

    def get_reset_password_token(self):
        auth_serializer = URLSafeTimedSerializer(
            secret_key=current_app.config['SECRET_KEY'], salt="password reset"
        )
        token = auth_serializer.dumps({'id': self.id})
        return token
    
    @staticmethod
    def verify_reset_password_token(token):
        auth_serializer = URLSafeTimedSerializer(
            secret_key=current_app.config['SECRET_KEY'], salt="password reset"
        )

        try:
            data = auth_serializer.loads(token, max_age=3600)
        except Exception as e:
            return None  # Invalid token
        
        user_id = data.get('id')

        if user_id is None:
            return None  # Invalid token structure
        
        return User.query.get(user_id)

    
    