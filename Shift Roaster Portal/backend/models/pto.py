# models/pto.py

from models import db

class PTO(db.Model):
    __tablename__ = 'ptos'  # Define the table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    analyst_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to users
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending, Approved, Rejected

    analyst = db.relationship('User', backref='ptos')