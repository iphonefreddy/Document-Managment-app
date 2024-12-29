
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    db.init_app(app)
    login_manager.init_app(app)

    # Import and register routes
    with app.app_context():
        from . import routes
        db.create_all()

    return app
