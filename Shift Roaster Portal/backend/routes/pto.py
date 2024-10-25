from flask import request, jsonify, Blueprint
from models import db
from models.pto import PTO
from models.user import User
from datetime import date, timedelta, datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('pto', __name__)


# Route to apply for PTO
@bp.route('/apply_pto', methods=['POST'])
@jwt_required()  # Ensures the user is authenticated
def apply_pto_route():
    try:
        # Get the current user's ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get data from the request
        data = request.get_json()
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Input validation
        if not start_date or not end_date:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Convert strings to date objects
        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
        
        # Ensure start date is not after end date
        if start_date > end_date:
            return jsonify({"error": "Start date cannot be after end date"}), 400

        # Get today's date
        today = date.today()
        
        # Get the first day of the next month
        first_day_next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        # Calculate the application deadline (5 days before the first day of next month)
        pto_application_deadline = first_day_next_month - timedelta(days=5)

        # Check if PTO is for the next month and applied before the deadline
        if start_date < first_day_next_month or today > pto_application_deadline:
            return jsonify({
                "error": f"PTO must be applied for next month and the deadline to apply is {pto_application_deadline.strftime('%Y-%m-%d')}."
            }), 400
        
        # Create new PTO request
        new_pto = PTO(
            analyst_id=current_user_id,  # Use the current user's ID as the analyst_id
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )
        
        # Save to the database
        db.session.add(new_pto)
        db.session.commit()
        
        # Success response
        return jsonify({"message": "PTO applied successfully", "pto_id": new_pto.id}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        # Rollback in case of any error
        db.session.rollback()
        return jsonify({"error": "Failed to apply for PTO", "details": str(e)}), 500
    

@bp.route('/my_ptos', methods=['GET'])
@jwt_required()  # Ensure that this route is only accessible to authenticated users
def view_my_ptos():
    # Get the authenticated user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Get the current date
    today = datetime.today().date()

    # Query PTOs applied by this analyst with a start date in the future
    future_ptos = PTO.query.filter_by(analyst_id=current_user_id).filter(PTO.start_date > today).all()

    # If no future PTOs are found, return an empty list
    if not future_ptos:
        return jsonify({"ptos": []}), 200

    # Format PTO data into a list of dictionaries
    pto_list = []
    for pto in future_ptos:
        pto_list.append({
            "pto_id": pto.id,
            "start_date": pto.start_date.isoformat(),
            "end_date": pto.end_date.isoformat(),
            "status": pto.status
        })

    return jsonify({"ptos": pto_list}), 200

@bp.route('/delete_pto', methods=['DELETE'])
@jwt_required()  # Ensure the user is authenticated
def delete_pto():
    # Get the authenticated user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Get the PTO ID from the request body
    data = request.get_json()
    pto_id = data.get('pto_id')

    # If no PTO ID is provided, return an error
    if not pto_id:
        return jsonify({"error": "PTO ID is required"}), 400

    # Find the PTO entry by its ID and analyst ID (current user)
    pto = PTO.query.filter_by(id=pto_id, analyst_id=current_user_id).first()

    # If the PTO does not exist or does not belong to the current user, return an error
    if not pto:
        return jsonify({"error": "PTO not found or unauthorized"}), 404

    # Delete the PTO
    db.session.delete(pto)
    db.session.commit()

    return jsonify({"message": "PTO deleted successfully"}), 200

@bp.route('/manage_pto', methods=['POST'])
@jwt_required()
def manage_pto():
    # Get the authenticated user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Get the PTO ID and action (approve/deny) from the request body
    data = request.get_json()
    pto_id = data.get('pto_id')
    action = data.get('action')  # Expected values: 'approve' or 'deny'

    if not pto_id or not action:
        return jsonify({"error": "PTO ID and action (approve/deny) are required"}), 400

    # Find the PTO request by ID
    pto = PTO.query.get(pto_id)
    if not pto:
        return jsonify({"error": "PTO not found"}), 404

    # Find the analyst who applied for the PTO
    analyst = User.query.get(pto.analyst_id)
    if not analyst:
        return jsonify({"error": "Analyst not found"}), 404

    # Get the manager's team ID
    manager = User.query.get(current_user_id)
    if not manager or manager.role != 'manager':
        return jsonify({"error": "You are not authorized to approve or deny this PTO request"}), 403
    
    # Check if the current user is the manager of the analyst's team
    if analyst.team_id != manager.team_id:
        return jsonify({"error": "You are not authorized to approve or deny this PTO request"}), 403

    # Update the status of the PTO request based on the action
    if action == 'approve':
        pto.status = 'Approved'
    elif action == 'deny':
        pto.status = 'Denied'
    else:
        return jsonify({"error": "Invalid action. Use 'approve' or 'deny'"}), 400

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": f"PTO request {action}d successfully"}), 200

# Route to get all PTO requests for the manager's team
@bp.route('/team_ptos', methods=['GET'])
@jwt_required()
def team_ptos():
    # Get the authenticated user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Find the user's details (analyst or manager)
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "Unauthorized access. You must be part of a team to view team PTOs."}), 403

    # Query for all analysts in the user's team (both analysts and managers are allowed)
    analysts = User.query.filter_by(team_id=user.team_id).all()

    # Get all PTOs for the analysts in the team
    pto_requests = PTO.query.filter(PTO.analyst_id.in_([analyst.id for analyst in analysts])).all()

    # Format the PTO data to return, including analyst name
    pto_list = [
        {
            "pto_id": pto.id,
            "analyst_id": pto.analyst_id,
            "analyst_name": next((analyst.username for analyst in analysts if analyst.id == pto.analyst_id), None),
            "start_date": pto.start_date.isoformat(),
            "end_date": pto.end_date.isoformat(),
            "status": pto.status,
        } for pto in pto_requests
    ]

    return jsonify({"pto_requests": pto_list}), 200