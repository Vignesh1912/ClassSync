from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from backend.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from backend.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from backend.routes.timetable import bp as timetable_bp
    app.register_blueprint(timetable_bp)

    from backend.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp)

    from backend.routes.assignment import bp as assignment_bp
    app.register_blueprint(assignment_bp)

    from backend.routes.announcement import bp as announcement_bp
    app.register_blueprint(announcement_bp)

    # Start the daily reminder scheduler (safe — won't crash if APScheduler missing)
    try:
        from backend.scheduler.reminders import start_scheduler
        start_scheduler(app)
    except Exception:
        pass

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))

    return app
