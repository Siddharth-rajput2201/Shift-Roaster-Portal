from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db  # Import db from models here

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shift_roaster.db'  # Using a relative path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this in production

    # Initialize the database
    db.init_app(app)

    # Initialize JWT Manager
    jwt = JWTManager(app)

    # Register Blueprints (routes)
    with app.app_context():
        from routes import shift, pto, auth, team  # Import routes within the app context
        app.register_blueprint(auth.bp ,url_prefix="/auth")
        app.register_blueprint(shift.bp,url_prefix="/shift")
        app.register_blueprint(pto.bp, url_prefix="/pto")
        app.register_blueprint(team.bp, url_prefix="/team")

        # Create database tables if they don't exist
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()  # Create the app instance
    app.run(debug=True)