from flask import request, Blueprint, jsonify
from models import db
from models.team import Team
from models.user import User

bp = Blueprint('team', __name__)

@bp.route('/add', methods=['POST'])
def add_team():
    data = request.get_json()

    # Validate the incoming data
    team_name = data.get('name')
    
    if not team_name:
        return ({"error": "Team name is required"}), 400

    # Check if team name already exists
    if Team.query.filter_by(name=team_name).first():
        return ({"error": "Team name already exists"}), 400

    # Create a new team entry
    new_team = Team(name=team_name)
    try:
        db.session.add(new_team)
        db.session.commit()
        return ({"message": "Team added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return ({"error": str(e)}), 500


@bp.route('/delete', methods=['DELETE'])
def delete_team_by_name():
    # Get team name from query parameter
    data = request.get_json()

    # Validate the incoming data
    team_name = data.get('name')


    if not team_name:
        return {"error": "Team name is required"}, 400

    # Find the team by name
    team = Team.query.filter_by(name=team_name).first()

    if not team:
        return {"error": "Team not found"}, 404

    # Delete the team and associated analysts
    try:
        # First, delete all users associated with the team
        User.query.filter_by(team_id=team.id).delete()
        # Then, delete the team itself
        db.session.delete(team)
        db.session.commit()
        return {"message": "Team and its users deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    

@bp.route('/update', methods=['PUT'])
def update_team():
    data = request.get_json()

    # Validate the incoming data
    current_team_name = data.get('current_name')
    new_team_name = data.get('new_name')

    if not current_team_name or not new_team_name:
        return ({"error": "Both current and new team names are required"}), 400

    # Check if the team exists
    team = Team.query.filter_by(name=current_team_name).first()
    if not team:
        return ({"error": "Team not found"}), 404

    # Check if the new team name already exists
    if Team.query.filter_by(name=new_team_name).first():
        return ({"error": "New team name already exists"}), 400

    # Update the team name
    team.name = new_team_name

    try:
        db.session.commit()
        return ({"message": "Team name updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return ({"error": str(e)}), 500
    
@bp.route('/all', methods=['GET'])
def get_all_teams():
    try:
        # Fetch all teams
        teams = Team.query.all()

        # Create a list of team names
        team_names = [{"id": team.id, "name": team.name} for team in teams]

        return jsonify({"teams": team_names}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/<int:team_id>/users', methods=['GET'])
def get_users_by_team(team_id):
    # Fetch the team by ID
    team = Team.query.get(team_id)
    
    if not team:
        return {"error": "Team not found"}, 404

    # Fetch all users belonging to this team
    users = User.query.filter_by(team_id=team_id).all()

    if not users:
        return {"message": "No users found in this team"}, 200

    # Create a list of users with relevant details
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "team_id": user.team_id
        }
        for user in users
    ]

    return {"team": team.name, "users": users_data}, 200