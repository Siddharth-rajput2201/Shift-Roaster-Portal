# utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from services.shift_service import assign_shifts
from models.team import Team

scheduler = BackgroundScheduler()

def prepare_roster():
    # Logic to prepare roster for all teams
    teams = Team.query.all()
    for team in teams:
        assign_shifts(team.id)

scheduler.add_job(func=prepare_roster, trigger='cron', day=26)
scheduler.start()