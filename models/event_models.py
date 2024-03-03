import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSONB

# Create SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    events_attended = db.Column(JSONB, default=list)  # Storing as JSON array
    events_organized = db.Column(JSONB, default=list)  # Storing as JSON array
    #local
    # events_organized = db.Column(db.JSON, default=list)  # Storing as JSON array in sqlite


class Event(db.Model):
    event_id = db.Column(db.Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = db.Column(db.Text, nullable=False)
    event_description = db.Column(db.Text, nullable=False)
    event_start_date = db.Column(db.Text, nullable=False)
    event_end_date = db.Column(db.Text, nullable=False)
    event_location = db.Column(db.Text, nullable=False)
    event_participants = db.Column(JSONB, default=list)  # Storing as JSON array
    event_organizer_id = db.Column(db.Text)  # Storing as JSON array
    event_organizer_name = db.Column(db.Text) 
    event_feedback = db.Column(db.JSON, default={})  # Stroing Feedback
    event_rating = db.Column(db.JSON, default={})  # Storing rating

class PasswordResetToken(db.Model):
    id = db.Column(db.Text, primary_key=True, default = lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Text, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    expiration_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow()+timedelta(minutes=15) ) # Define the expiration duration
