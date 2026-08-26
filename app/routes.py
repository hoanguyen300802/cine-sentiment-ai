"""
Application Route Handlers
Implements multi-language routing, TMDb search listing, genre filtering,
movie categories (popular, now_playing, upcoming, top_rated), popular people,
awards hall of fame, movie details, and sentiment AI endpoints.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
from app.api_config import (
    search_movies,
    get_genres,
    get_movies_by_genre,
    get_movies_by_category,
    get_popular_movies,
    get_popular_people,
    get_movie_details_by_id,
    get_movie_info
)
from app.sentiment_analysis import analyze_sentiment
from app.translations import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, get_translations, get_tmdb_language


@app.context_processor
def inject_global_template_vars():
    """
    Injects active language dictionary and supported languages into all templates.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    if current_lang not in SUPPORTED_LANGUAGES:
        current_lang = DEFAULT_LANGUAGE

    t = get_translations(current_lang)
    return dict(
        t=t,
        current_lang=current_lang,
        supported_langs=SUPPORTED_LANGUAGES,
        supported_languages=SUPPORTED_LANGUAGES,
        active_lang_info=SUPPORTED_LANGUAGES[current_lang]
    )


@app.route('/set_language', methods=['GET'])
@app.route('/set_language/<lang_code>', methods=['GET'])
def set_language(lang_code=None):
    """
    Switches active language stored in session and redirects back to previous page.
    """
    selected = lang_code or request.args.get('lang')
    if selected and selected in SUPPORTED_LANGUAGES:
        session['lang'] = selected
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def index():
    """
    Home page: renders spotlight search bar, genre tags, and trending/popular movies.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    genres = get_genres(language=tmdb_lang)
    popular_movies = get_popular_movies(language=tmdb_lang)

    return render_template('index.html', genres=genres, popular_movies=popular_movies)


@app.route('/movies/<category>')
def movie_category(category):
    """
    Renders movies by category: popular, now_playing, upcoming, top_rated.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)
    t = get_translations(current_lang)

    category_titles = {
        'popular': t.get('nav_popular_movies', 'Popular Movies'),
        'now_playing': t.get('nav_now_playing', 'Now Playing in Theaters'),
        'upcoming': t.get('nav_upcoming', 'Upcoming Movies'),
        'top_rated': t.get('nav_top_rated', 'Top Rated Masterpieces'),
    }

    title = category_titles.get(category, t.get('nav_movies', 'Movies'))
    movies = get_movies_by_category(category, language=tmdb_lang)

    return render_template(
        'search_results.html',
        movies=movies,
        search_query=title,
        result_title=title,
        is_genre=False
    )


@app.route('/people')
def people():
    """
    Displays the Popular People (Actors, Directors, Celebrities) page.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    people_list = get_popular_people(language=tmdb_lang)

    return render_template('people.html', people=people_list)


@app.route('/awards')
def awards():
    """
    Displays the Awards & Masterpieces Hall of Fame page.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    top_movies = get_movies_by_category('top_rated', language=tmdb_lang)

    return render_template('awards.html', movies=top_movies)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Searches TMDb and returns a list of matching movies.
    """
    if request.method == 'POST':
        query = request.form.get('movie_name', '').strip()
    else:
        query = request.args.get('q', '').strip()

    if not query:
        return redirect(url_for('index'))

    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    movies = search_movies(query, language=tmdb_lang)

    if not movies:
        return render_template('error.html', error_type='not_found', query=query)

    return render_template(
        'search_results.html',
        movies=movies,
        search_query=query,
        result_title=None,
        is_genre=False
    )


@app.route('/genre/<int:genre_id>')
def genre_movies(genre_id):
    """
    Discovers and displays movies belonging to a specific genre.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    genres = get_genres(language=tmdb_lang)
    genre_name = next((g['name'] for g in genres if g['id'] == genre_id), f'Genre #{genre_id}')

    movies = get_movies_by_genre(genre_id, language=tmdb_lang)

    if not movies:
        return render_template('error.html', error_type='not_found', query=genre_name)

    return render_template(
        'search_results.html',
        movies=movies,
        search_query=genre_name,
        result_title=genre_name,
        is_genre=True,
        genre_id=genre_id,
        genres=genres
    )


@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """
    Displays full details for a selected movie by its ID,
    including actors/cast, YouTube trailer, and the interactive Sentiment AI.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    movie_info = get_movie_details_by_id(movie_id, language=tmdb_lang)

    if not movie_info:
        return render_template('error.html', error_type='not_found', query=f'Movie #{movie_id}')

    return render_template('result.html', movie_info=movie_info)


@app.route('/analyze_sentiment', methods=['POST'])
def analyze_review():
    """
    AJAX / Form endpoint for real-time sentiment analysis.
    Robustly handles all parameter formats (review, review_text, user_review).
    """
    if request.is_json:
        data = request.get_json() or {}
        review_text = data.get('review_text') or data.get('review') or data.get('user_review', '')
    else:
        review_text = request.form.get('review_text') or request.form.get('user_review') or request.form.get('review', '')

    result = analyze_sentiment(review_text)

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'data': result,
            **result
        })

    movie_id = request.form.get('movie_id')
    if movie_id:
        return redirect(url_for('movie_detail', movie_id=movie_id))
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_type='404'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_type='500'), 500
