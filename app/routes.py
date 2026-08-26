"""
Application Route Handlers
Implements clean routing, multi-language switching, TMDb discovery, and sentiment AI endpoints.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
from app.api_config import get_movie_info
from app.sentiment_analysis import analyze_sentiment
from app.translations import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    get_translations,
    get_tmdb_language
)


@app.context_processor
def inject_global_variables():
    """Inject language settings and translations into all Jinja2 templates."""
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    if current_lang not in SUPPORTED_LANGUAGES:
        current_lang = DEFAULT_LANGUAGE
        session['lang'] = current_lang
        
    return {
        'current_lang': current_lang,
        'supported_langs': SUPPORTED_LANGUAGES,
        't': get_translations(current_lang)
    }


@app.route('/')
def index():
    """Home landing page with hero spotlight search and recent searches."""
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    """Search for movie details via TMDb and present the result view."""
    if request.method == 'POST':
        movie_name = request.form.get('movie_name', '').strip()
    else:
        movie_name = request.args.get('movie_name', '').strip()

    if not movie_name:
        return redirect(url_for('index'))

    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)
    
    movie_info = get_movie_info(movie_name, language=tmdb_lang)

    if not movie_info:
        return render_template(
            'error.html',
            error_type='not_found',
            query=movie_name
        ), 404

    return render_template(
        'result.html',
        movie_info=movie_info,
        query=movie_name,
        user_review=None,
        sentiment_data=None
    )


@app.route('/analyze_sentiment', methods=['POST'])
def analyze_review():
    """
    Analyzes movie review text.
    Supports both asynchronous AJAX requests and traditional form submissions.
    """
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.accept_mimetypes

    if request.is_json:
        data = request.get_json()
        user_review = data.get('review', '').strip()
        movie_name = data.get('movie_name', '').strip()
    else:
        user_review = request.form.get('user_review', request.form.get('review', '')).strip()
        movie_name = request.form.get('movie_name', '').strip()

    if not user_review:
        if is_ajax:
            return jsonify({'success': False, 'error': 'Empty review'}), 400
        return redirect(url_for('search_movie', movie_name=movie_name))

    # Execute NLP Sentiment Analysis
    sentiment_data = analyze_sentiment(user_review)

    if is_ajax:
        return jsonify({
            'success': True,
            'review': user_review,
            'data': sentiment_data
        })

    # Non-AJAX fallback: render full template with result
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)
    movie_info = get_movie_info(movie_name, language=tmdb_lang) if movie_name else None

    return render_template(
        'result.html',
        movie_info=movie_info,
        query=movie_name,
        user_review=user_review,
        sentiment_data=sentiment_data
    )


@app.route('/set_language/<lang>')
def set_language(lang):
    """Switch user interface and data language."""
    if lang in SUPPORTED_LANGUAGES:
        session['lang'] = lang
    
    # Redirect back to the previous page or home
    referrer = request.referrer
    if referrer and ('/search' in referrer or '/set_language' not in referrer):
        return redirect(referrer)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 handler."""
    return render_template('error.html', error_type='404'), 404


@app.errorhandler(500)
def server_error(e):
    """Custom 500 handler."""
    return render_template('error.html', error_type='500'), 500
