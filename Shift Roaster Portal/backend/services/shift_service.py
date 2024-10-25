# services/shift_service.py
from models import db
from models.shift import Shift
from models.user import User
from models.team import Team
from datetime import date, timedelta
import calendar

def assign_shifts(team_id):
    """
    Assign shifts to a team's analysts, ensuring:
    1. Even distribution across shifts.
    2. At least two analysts on the Night shift.
    3. Monthly shift rotation in the order: Night → Afternoon → Morning → Night.
    """
    team = Team.query.get(team_id)
    if not team:
        return {"error": "Team not found"}, 404
    
    analysts = User.query.filter_by(team_id=team_id, role='analyst').all()
    if not analysts:
        return {"error": "No analysts available in the team"}
    
    num_analysts = len(analysts)
    if num_analysts < 3:
        return {"error": "Not enough analysts to assign shifts"}

    # Rotational shift assignment logic
    shifts = ['Night', 'Afternoon', 'Morning']
    assignments = []
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    # Create shift assignments for the month
    for day in range(1, days_in_month + 1):
        current_date = today.replace(day=day)
        
        # Night shift assignments
        night_shift_analysts = analysts[:2]  # At least 2 analysts for Night shift
        for analyst in night_shift_analysts:
            new_shift = Shift(name='Night', analyst_id=analyst.id, team_id=team_id, shift_date=current_date)
            db.session.add(new_shift)
            assignments.append({'date': current_date, 'analyst': analyst.username, 'shift': 'Night'})

        # Afternoon shift assignments
        afternoon_shift_analysts = analysts[2:3]  # At least 1 analyst for Afternoon shift
        for analyst in afternoon_shift_analysts:
            new_shift = Shift(name='Afternoon', analyst_id=analyst.id, team_id=team_id, shift_date=current_date)
            db.session.add(new_shift)
            assignments.append({'date': current_date, 'analyst': analyst.username, 'shift': 'Afternoon'})

        # Morning shift assignments
        morning_shift_analysts = analysts[3:]  # Remaining analysts for Morning shift
        for analyst in morning_shift_analysts:
            new_shift = Shift(name='Morning', analyst_id=analyst.id, team_id=team_id, shift_date=current_date)
            db.session.add(new_shift)
            assignments.append({'date': current_date, 'analyst': analyst.username, 'shift': 'Morning'})

        # Rotate analysts for next day (shift rotation logic)
        analysts = analysts[1:] + analysts[:1]  # Rotate the list of analysts

    db.session.commit()
    return {"assignments": assignments}