from flask import request, jsonify, Blueprint
from models import db
from models.shift import Shift
from models.user import User
from models.team import Team
from models.pto import PTO
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

bp = Blueprint('shift', __name__)

from datetime import datetime

@bp.route('/assign_shift', methods=['POST'])
@jwt_required()
def assign_shift():
    # Get the current user's information from the JWT token
    current_user = get_jwt_identity()

    # Check if the user is a manager
    manager = User.query.get(current_user)  # Get the user by ID
    if not manager or manager.role != 'manager':
        return jsonify({"error": "You are not authorized to assign shifts."}), 403    

    # Get the list of shift assignments from the request
    assignments = request.get_json()

    # Loop through each assignment
    for data in assignments:
        analyst_id = data.get('analyst_id')
        shift_name = data.get('shift_name')  # Shift type (Morning, Afternoon, Night)
        week_off = data.get('week_off')
        start_date = data.get('start_date')  # Start date from the request
        end_date = data.get('end_date')  # End date from the request

        # Validate required fields
        if not shift_name:
            return {"error": "Shift name is required."}, 400
        if not start_date or not end_date:
            return {"error": "Start date and end date are required."}, 400

        # Convert the start_date and end_date from string to datetime
        try:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

            # Check if the end date is after the start date
            if end_date_dt <= start_date_dt:
                return {"error": "End date must be after start date."}, 400

        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD."}, 400

        # Create a new shift and save to the database
        new_shift = Shift(
            analyst_id=analyst_id,
            team_id=manager.team_id,  # Fetch manager's team_id from JWT
            name=shift_name,  # Store the shift type
            week_off=week_off,  # Store week off
            start_date=start_date_dt,  # Use the provided start date
            end_date=end_date_dt  # Use the provided end date
        )
        db.session.add(new_shift)

    db.session.commit()

    return {"message": "Shifts assigned successfully."}, 201
    

@bp.route('/myshift', methods=['POST'])
@jwt_required()
def get_shifts():
    # Get the current user's ID from the JWT token
    current_user_id = get_jwt_identity()
     # Assuming the analyst ID is stored in the JWT payload

    # Fetch shifts assigned to the analyst with valid start and end dates
    shifts = Shift.query.filter(
        Shift.analyst_id == current_user_id,
    ).all()

    # If no shifts are found
    if not shifts:
        return {"message": "No shifts found for this analyst."}, 404

    # Prepare the response data
    shift_data = []
    for shift in shifts:
        shift_data.append({
            "id": shift.id,
            "team_id": shift.team_id,
            "shift_name": shift.name,
            "week_off": shift.week_off,
            "start_date": shift.start_date,
            "end_date": shift.end_date
        })

    return {"shifts": shift_data}, 200

@bp.route('/delete_shift', methods=['DELETE'])
@jwt_required()
def delete_shift():
    # Get the current user's information from the JWT token
    current_user = get_jwt_identity()

    # Check if the user is a manager
    manager = User.query.get(current_user)
    if not manager or manager.role != 'manager':
        return jsonify({"error": "You are not authorized to delete shifts."}), 403

    data = request.get_json()
    shift_id = data.get('shift_id')

    # Validate the shift ID
    if not shift_id:
        return {"error": "Shift ID is required."}, 400

    # Find the shift by ID
    shift = Shift.query.get(shift_id)
    
    # If the shift does not exist
    if not shift:
        return {"error": "Shift not found."}, 404

    # Delete the shift
    db.session.delete(shift)
    db.session.commit()

    return {"message": "Shift deleted successfully."}, 200

@bp.route('/team_shifts', methods=['POST'])
@jwt_required()
def get_team_shifts():
    # Get the current user's information from the JWT token
    current_user = get_jwt_identity()

    # Fetch the user details from the database (to get team information)
    user = User.query.get(current_user)

    # Check if the user is part of a team
    if not user or not user.team_id:
        return jsonify({"error": "You are not part of any team."}), 403

    team_id = user.team_id  # Fetch the team ID from the user object

    # Fetch all shifts for the members of the team, joining with User to get names
    shifts = Shift.query.filter(Shift.team_id == team_id).all()

    # If no shifts are found
    if not shifts:
        return jsonify({"message": "No shifts found for this team."}), 404

    # Fetch approved PTOs for all analysts in the team
    approved_ptos = PTO.query.filter(
        PTO.analyst_id.in_([shift.analyst_id for shift in shifts]),
        PTO.status == "Approved"
    ).all()

    # Prepare a dictionary to store PTO details by analyst_id
    pto_details = {}
    for pto in approved_ptos:
        if pto.analyst_id not in pto_details:
            pto_details[pto.analyst_id] = []
        pto_details[pto.analyst_id].append({
            "pto_id": pto.id,
            "start_date": pto.start_date,
            "end_date": pto.end_date
        })

    # Prepare the response data
    shift_data = []
    for shift in shifts:
        analyst = shift.analyst  # Access the related User instance directly
        shift_data.append({
            "analyst_name": analyst.username,
            "shift_id": shift.id,
            "shift_name": shift.name,
            "week_off": shift.week_off,
            "start_date": shift.start_date,
            "end_date": shift.end_date,
            "approved_ptos": pto_details.get(analyst.id, [])
        })

    return jsonify({"team_shifts": shift_data}), 200

@bp.route('/new_team_shifts', methods=['POST'])
@jwt_required()
def new_get_team_shifts():
    # Get the current user's information from the JWT token
    current_user = get_jwt_identity()

    # Fetch the user details from the database (to get team information)
    user = User.query.get(current_user)

    # Check if the user is part of a team
    if not user or not user.team_id:
        return jsonify({"error": "You are not part of any team."}), 403

    team_id = user.team_id  # Fetch the team ID from the user object

    # Fetch all shifts for the members of the team, joining with User to get names
    shifts = Shift.query.filter(Shift.team_id == team_id).all()

    # If no shifts are found
    if not shifts:
        return jsonify({"message": "No shifts found for this team."}), 404

    # Fetch approved PTOs for all analysts in the team
    approved_ptos = PTO.query.filter(
        PTO.analyst_id.in_([shift.analyst_id for shift in shifts]),
        PTO.status == "Approved"
    ).all()

    # Prepare a dictionary to store PTO details by analyst_id
    pto_details = {}
    for pto in approved_ptos:
        if pto.analyst_id not in pto_details:
            pto_details[pto.analyst_id] = []
        
        # Get all dates for the PTO
        pto_dates = get_all_dates(pto.start_date, pto.end_date)
        pto_details[pto.analyst_id].extend(pto_dates)

    # Prepare the response data
    shift_data = []
    for shift in shifts:
        analyst = shift.analyst  # Access the related User instance directly
        shift_data.append({
            "analyst_name": analyst.username,
            "shift_id": shift.id,
            "shift_name": shift.name,
            "week_off": shift.week_off,
            "start_date": shift.start_date,
            "end_date": shift.end_date,
            "approved_ptos": pto_details.get(analyst.id, [])  # List of dates instead of start/end
        })

    return jsonify({"team_shifts": shift_data}), 200

def get_all_dates(start_date, end_date):
    """
    Utility function to generate all dates between start_date and end_date (inclusive).
    If start_date == end_date, it returns only that date.
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))  # Format date as string 'YYYY-MM-DD'
        current_date += timedelta(days=1)  # Increment the date by one day

    return dates