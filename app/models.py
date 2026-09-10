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

    def __init__(
        self,
        username=None,
        email=None,
        password=None,
        password_hash=None,
        display_name=None,
        avatar_url=None,
        bio=None,
        created_at=None,
        last_login=None,
        is_admin=False,
        **kwargs
    ):
        super().__init__(**kwargs)
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if password_hash is not None:
            self.password_hash = password_hash
        elif password is not None:
            self.set_password(password)
        if display_name is not None:
            self.display_name = display_name
        if avatar_url is not None:
            self.avatar_url = avatar_url
        if bio is not None:
            self.bio = bio
        if created_at is not None:
            self.created_at = created_at
        if last_login is not None:
            self.last_login = last_login
        self.is_admin = is_admin
        for k, v in kwargs.items():
            setattr(self, k, v)

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

    def __init__(
        self,
        user_id=None,
        movie_id=None,
        movie_title=None,
        poster_url=None,
        rating=0.0,
        year=None,
        added_at=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if movie_id is not None:
            self.movie_id = movie_id
        if movie_title is not None:
            self.movie_title = movie_title
        if poster_url is not None:
            self.poster_url = poster_url
        self.rating = rating if rating is not None else 0.0
        if year is not None:
            self.year = year
        if added_at is not None:
            self.added_at = added_at
        for k, v in kwargs.items():
            setattr(self, k, v)

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

    def __init__(
        self,
        user_id=None,
        movie_id=None,
        movie_title=None,
        review_text=None,
        sentiment=None,
        polarity=0.0,
        subjectivity=0.0,
        positive_pct=0.0,
        neutral_pct=0.0,
        negative_pct=0.0,
        tone_description=None,
        detected_lang_name=None,
        created_at=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if movie_id is not None:
            self.movie_id = movie_id
        if movie_title is not None:
            self.movie_title = movie_title
        if review_text is not None:
            self.review_text = review_text
        if sentiment is not None:
            self.sentiment = sentiment
        self.polarity = polarity if polarity is not None else 0.0
        self.subjectivity = subjectivity if subjectivity is not None else 0.0
        self.positive_pct = positive_pct if positive_pct is not None else 0.0
        self.neutral_pct = neutral_pct if neutral_pct is not None else 0.0
        self.negative_pct = negative_pct if negative_pct is not None else 0.0
        if tone_description is not None:
            self.tone_description = tone_description
        if detected_lang_name is not None:
            self.detected_lang_name = detected_lang_name
        if created_at is not None:
            self.created_at = created_at
        for k, v in kwargs.items():
            setattr(self, k, v)

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
