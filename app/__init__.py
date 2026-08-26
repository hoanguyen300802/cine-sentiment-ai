"""
Flask Application Factory and Package Initialization
"""

import os
import werkzeug
from flask import Flask
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

# Import routes after app initialization to prevent circular dependencies
from app import routes
