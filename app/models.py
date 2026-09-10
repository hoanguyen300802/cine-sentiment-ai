"""
Database Models for CineSentiment AI
Includes User accounts, User Watchlist, and Review Sentiment History.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """
    User model representing registered web users.
    Inherits from UserMixin for Flask-Login compatibility.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    watchlist_items = db.relationship(
        'Watchlist',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    reviews = db.relationship(
        'ReviewHistory',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        """Hashes the password securely with pbkdf2:sha256."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a plain text password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def get_display_name(self):
        """Returns display name if set, else username."""
        return self.display_name or self.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.get_display_name(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'watchlist_count': self.watchlist_items.count(),
            'reviews_count': self.reviews.count(),
            'is_admin': self.is_admin,
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Watchlist(db.Model):
    """
    User Watchlist model for saving favorite movies.
    """
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, nullable=False, index=True)
    movie_title = db.Column(db.String(255), nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Float, default=0.0)
    year = db.Column(db.String(10), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_watchlist'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'movie_title': self.movie_title,
            'poster_url': self.poster_url,
            'rating': self.rating,
            'year': self.year,
            'added_at': self.added_at.strftime('%Y-%m-%d %H:%M:%S') if self.added_at else None
        }

    def __repr__(self):
        return f'<Watchlist user={self.user_id} movie={self.movie_id}>'


class ReviewHistory(db.Model):
    """
    History of sentiment reviews analyzed on the platform.
    Can be linked to a registered user and a movie.
    """
    __tablename__ = 'review_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    movie_id = db.Column(db.Integer, nullable=True, index=True)
    movie_title = db.Column(db.String(255), nullable=True)
    review_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)  # positive, neutral, negative
    polarity = db.Column(db.Float, default=0.0)
    subjectivity = db.Column(db.Float, default=0.0)
    positive_pct = db.Column(db.Float, default=0.0)
    neutral_pct = db.Column(db.Float, default=0.0)
    negative_pct = db.Column(db.Float, default=0.0)
    tone_description = db.Column(db.String(100), nullable=True)
    detected_lang_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'movie_title': self.movie_title,
            'review_text': self.review_text,
            'sentiment': self.sentiment,
            'polarity': self.polarity,
            'subjectivity': self.subjectivity,
            'positive_pct': self.positive_pct,
            'neutral_pct': self.neutral_pct,
            'negative_pct': self.negative_pct,
            'tone_description': self.tone_description,
            'detected_lang_name': self.detected_lang_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<ReviewHistory id={self.id} sentiment={self.sentiment}>'
