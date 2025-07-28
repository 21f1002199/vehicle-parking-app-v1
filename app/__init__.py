# app/__init__.py
from flask import Flask
from .extensions import db, login_manager
from .models import User
from .views.routes import main as main_blueprint
from werkzeug.security import generate_password_hash
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Enable SQLite foreign key constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    login_manager.init_app(app)
    

    from .views.routes import init_routes
    init_routes(app)

    app.register_blueprint(main_blueprint)

    with app.app_context():
        from sqlalchemy import text
        db.session.execute(text("PRAGMA foreign_keys=ON"))
        db.create_all()

        # Default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin',
                full_name='Admin User',
                address='Admin HQ',
                pin_code='000000',
                email='admin@example.com',
                phone_number='9999999999'
            )
            db.session.add(admin)
            db.session.commit()

    return app

