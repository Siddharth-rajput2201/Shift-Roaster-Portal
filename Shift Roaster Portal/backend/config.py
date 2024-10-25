import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/shift_roaster.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')