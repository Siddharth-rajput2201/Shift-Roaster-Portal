# models/team.py

from models import db

class Team(db.Model):
    __tablename__ = 'teams'  # Define the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # Define relationship with User model
    analysts = db.relationship('User', backref='team', lazy=True)