# models/shift.py

from models import db

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)  # Morning, Afternoon, Night
    analyst_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to users
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)  # Reference to teams
    start_date = db.Column(db.Date, nullable=True)  # Start date of the shift
    end_date = db.Column(db.Date, nullable=True)    # End date of the shift
    week_off = db.Column(db.String(20), nullable=False)  # Store week off as a string (e.g., "Sunday-Monday")

    analyst = db.relationship('User', backref='shifts')
    team = db.relationship('Team', backref='team_shifts')