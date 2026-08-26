"""
Main Application Entrypoint
Run with:
    python manage.py
"""

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print(" CineSentiment AI - Movie Discovery & Sentiment Intelligence ")
    print(" Server running on: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
