from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user') # admin, staff, user
    status = db.Column(db.String(20), nullable=False, default='approved') # pending, approved, blacklisted

    # Relationships
    treks_managed = db.relationship('Trek', backref='manager', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # Easy, Moderate, Hard
    duration = db.Column(db.Integer, nullable=False) # In days
    available_slots = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open') # Open, Closed, Completed
    description = db.Column(db.Text, nullable=True)
    
    # Foreign Key for Staff Manager
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Booked') # Booked, Cancelled, Completed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

