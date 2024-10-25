# models/user.py

from models import db
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'  # Define the table name explicitly
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Either 'manager' or 'analyst'
    
    # Foreign key to Team (only for analysts)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)  # Reference to teams

    def __init__(self, username, password, role, team_id=None):
        self.username = username
        self.password_hash = generate_password_hash(password).decode('utf8')
        self.role = role
        self.team_id = team_id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}, Role: {self.role}, Team ID: {self.team_id}>"
    

