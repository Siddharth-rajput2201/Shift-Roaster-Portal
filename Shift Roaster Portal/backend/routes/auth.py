# routes/auth.py

from flask import request, Blueprint
from models import db
from models.user import User
from models.team import Team
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    team_id = data.get('team_id')  # The selected team from the dropdown

    # Validate fields
    if not username or not password or not role or not team_id:
        return {"error": "Missing required fields"}, 400
    
    # Check if team exists
    team = Team.query.get(team_id)
    if not team:
        return {"error": "Team does not exist"}, 404

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return {"error": "Username already taken"}, 409

    # Create and save the new user (hashing happens in the User model)
    new_user = User(username=username, password=password, role=role, team_id=team_id)
    db.session.add(new_user)
    db.session.commit()

    return {"message": "User created successfully", "user_id": new_user.id}, 201



@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Find the user by username
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Generate access token using the user's ID
        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200
    else:
        # Return error if credentials are invalid
        return {"error": "Invalid credentials"}, 401

from flask_jwt_extended import jwt_required, get_jwt_identity

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return {"error": "User not found"}, 404

    # Return the user ID and role (analyst/manager) to the frontend
    return {"user_id": current_user_id, "role": user.role,"team_id":user.team_id}, 200