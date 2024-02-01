from app.extensions import db
from flask_login import UserMixin
from scripts.utils import sha256_hash
from datetime import datetime
import secrets


class MonitoredAd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_number = db.Column(db.String(100), nullable=False)
    website_url = db.Column(db.String(255), nullable=False)
    occurrence_count = db.Column(db.Integer, default=0)  # New field to store the count
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # You can add additional fields as needed, e.g., last_checked_at, notification_status, etc.

    # Foreign Key to refer to the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    password_salt = db.Column(db.String(32), nullable=False)
    whatsapp = db.Column(db.Integer)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # User can have many MonitoredAd
    monitored_ads = db.relationship('MonitoredAd', backref='user')

    
    def __repr__(self):
        return f"User(id={self.id}, fullname={self.fullname}, email={self.email}, whatsapp={self.whatsapp}, is_admin={self.is_admin}, created_at={self.created_at})"

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
    
    