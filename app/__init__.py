"""
Flask Application Factory and Package Initialization
"""

import os
import werkzeug
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

# Werkzeug 3.x compatibility patch for Flask test client / headers
if not hasattr(werkzeug, '__version__'):
    try:
        import importlib.metadata
        werkzeug.__version__ = importlib.metadata.version('werkzeug')
    except Exception:
        werkzeug.__version__ = '3.0.0'

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_cine_sentiment_secret_2026')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Database Configuration (SQLite in instance folder)
os.makedirs(app.instance_path, exist_ok=True)
db_path = os.path.join(app.instance_path, 'cinesentiment.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
from app.models import db, User
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this feature.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


# Register Blueprints
from app.auth import auth_bp
from app.watchlist_routes import watchlist_bp
app.register_blueprint(auth_bp)
app.register_blueprint(watchlist_bp)

# Create database tables automatically
with app.app_context():
    db.create_all()

# Import routes after app initialization to prevent circular dependencies
from app import routes

