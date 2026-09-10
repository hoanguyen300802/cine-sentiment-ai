"""
Watchlist & Review History Blueprint for CineSentiment AI
Allows users to save favorite movies, toggle bookmarks, and view analysis history.
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from app.models import db, Watchlist, ReviewHistory
from app.telegram_bot import telegram_bot
from app.translations import get_translations, DEFAULT_LANGUAGE

watchlist_bp = Blueprint('watchlist_bp', __name__)


@watchlist_bp.route('/watchlist')
@login_required
def view_watchlist():
    """Renders user's personal movie watchlist."""
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    t = get_translations(current_lang)

    sort_by = request.args.get('sort', 'newest')
    query = Watchlist.query.filter_by(user_id=current_user.id)

    if sort_by == 'rating':
        items = query.order_by(Watchlist.rating.desc()).all()
    elif sort_by == 'title':
        items = query.order_by(Watchlist.movie_title.asc()).all()
    else:  # newest
        items = query.order_by(Watchlist.added_at.desc()).all()

    return render_template('watchlist.html', watchlist=items, current_sort=sort_by)


@watchlist_bp.route('/api/watchlist/toggle', methods=['POST'])
@login_required
def toggle_watchlist():
    """
    AJAX endpoint to add or remove a movie from user's watchlist.
    """
    data = request.get_json(silent=True) or {}
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title', 'Unknown Title')
    poster_url = data.get('poster_url')
    rating = float(data.get('rating', 0.0)) if data.get('rating') else 0.0
    year = str(data.get('year', 'N/A'))

    if not movie_id:
        return jsonify({'success': False, 'message': 'Missing movie_id'}), 400

    existing = Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        in_watchlist = False
        action_msg = "Removed from Watchlist"
    else:
        new_item = Watchlist(
            user_id=current_user.id,
            movie_id=movie_id,
            movie_title=movie_title,
            poster_url=poster_url,
            rating=rating,
            year=year
        )
        db.session.add(new_item)
        db.session.commit()
        in_watchlist = True
        action_msg = "Added to Watchlist"
        # Notify via Telegram bot if enabled
        telegram_bot.notify_watchlist_added(current_user, movie_title, movie_id)

    new_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    return jsonify({
        'success': True,
        'in_watchlist': in_watchlist,
        'message': action_msg,
        'count': new_count
    })


@watchlist_bp.route('/api/watchlist/check/<int:movie_id>')
def check_watchlist(movie_id):
    """Checks if a movie is bookmarked by current user."""
    if not current_user.is_authenticated:
        return jsonify({'in_watchlist': False})

    exists = Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first() is not None

    return jsonify({'in_watchlist': exists})


@watchlist_bp.route('/my-reviews')
@login_required
def my_reviews():
    """Displays the history of sentiment reviews analyzed by the user."""
    sentiment_filter = request.args.get('filter', 'all')
    query = ReviewHistory.query.filter_by(user_id=current_user.id)

    if sentiment_filter in ('positive', 'neutral', 'negative'):
        query = query.filter_by(sentiment=sentiment_filter)

    reviews = query.order_by(ReviewHistory.created_at.desc()).all()

    # Calculate summary metrics
    total = len(reviews)
    pos_count = sum(1 for r in reviews if r.sentiment == 'positive')
    neg_count = sum(1 for r in reviews if r.sentiment == 'negative')
    neu_count = sum(1 for r in reviews if r.sentiment == 'neutral')
    avg_polarity = round(sum(r.polarity for r in reviews) / total, 2) if total > 0 else 0.0

    return render_template(
        'my_reviews.html',
        reviews=reviews,
        total=total,
        pos_count=pos_count,
        neg_count=neg_count,
        neu_count=neu_count,
        avg_polarity=avg_polarity,
        current_filter=sentiment_filter
    )


@watchlist_bp.route('/api/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Deletes a review from the user's personal review history."""
    item = ReviewHistory.query.filter_by(id=review_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Review not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Review removed from history'})
