# services/pto_service.py

from models import db
from models.pto import PTO
from datetime import date, timedelta
from flask import request, jsonify, Blueprint
from models import db
from models.user import User  # Assuming User model is in models.user


bp = Blueprint('pto', __name__)


def approve_pto(pto_id, data):
    pto = PTO.query.get(pto_id)
    if not pto:
        return {"error": "PTO not found"}, 404
    
    new_status = data.get('status')
    if new_status not in ['Approved', 'Rejected']:
        return {"error": "Invalid status"}, 400
    
    pto.status = new_status
    db.session.commit()
    
    return {"message": f"PTO {new_status} successfully"}