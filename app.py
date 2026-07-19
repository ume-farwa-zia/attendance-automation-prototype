"""
SafeX AI Attendance Automation — Flask application entrypoint.

Run:
    python app.py
Then open http://127.0.0.1:5000/ for the employee check-in page,
or use http://127.0.0.1:5000/manager/login to access the manager dashboard.
"""
from flask import Flask

from config import Config
from database.db import init_db
from routes.api_routes import api_bp
from routes.attendance_routes import attendance_bp
from routes.dashboard_routes import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        init_db()

    app.register_blueprint(attendance_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
