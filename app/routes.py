"""
Application Route Handlers
Implements multi-language routing, TMDb search listing, genre filtering,
movie categories (popular, now_playing, upcoming, top_rated), popular people,
awards hall of fame, movie details with similar movies & TMDb reviews,
sentiment AI endpoints with DB history and Telegram alert integration.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import current_user
from app import app
from app.models import db, Watchlist, ReviewHistory
from app.telegram_bot import telegram_bot
from app.api_config import (
    search_movies,
    search_movies_paginated,
    get_genres,
    get_movies_by_genre,
    get_movies_by_genre_paginated,
    get_movies_by_category,
    get_movies_by_category_paginated,
    get_popular_movies,
    get_popular_people,
    search_people,
    get_person_details,
    get_award_by_slug,
    get_movie_details_by_id,
    get_similar_movies,
    get_movie_reviews_tmdb,
    get_movie_info
)
from app.awards_data import get_all_awards
from app.sentiment_analysis import analyze_sentiment
from app.translations import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, get_translations, get_tmdb_language


@app.context_processor
def inject_global_template_vars():
    """
    Injects active language dictionary, user states, and app meta into all templates.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    if current_lang not in SUPPORTED_LANGUAGES:
        current_lang = DEFAULT_LANGUAGE

    t = get_translations(current_lang)

    user_watchlist_count = 0
    if current_user.is_authenticated:
        try:
            user_watchlist_count = current_user.watchlist_items.count()
        except Exception:
            user_watchlist_count = 0

    return dict(
        t=t,
        current_lang=current_lang,
        supported_langs=SUPPORTED_LANGUAGES,
        supported_languages=SUPPORTED_LANGUAGES,
        active_lang_info=SUPPORTED_LANGUAGES[current_lang],
        user_watchlist_count=user_watchlist_count,
        telegram_configured=telegram_bot.is_configured()
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
    Renders movies by category: popular, now_playing, upcoming, top_rated with pagination.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)
    t = get_translations(current_lang)
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    category_titles = {
        'popular': t.get('nav_popular_movies', 'Popular Movies'),
        'now_playing': t.get('nav_now_playing', 'Now Playing in Theaters'),
        'upcoming': t.get('nav_upcoming', 'Upcoming Movies'),
        'top_rated': t.get('nav_top_rated', 'Top Rated Masterpieces'),
    }

    title = category_titles.get(category, t.get('nav_movies', 'Movies'))
    paginated_data = get_movies_by_category_paginated(category, language=tmdb_lang, page=page)

    return render_template(
        'search_results.html',
        movies=paginated_data['movies'],
        search_query=title,
        result_title=title,
        is_genre=False,
        category=category,
        pagination={
            'page': paginated_data['page'],
            'total_pages': paginated_data['total_pages'],
            'total_results': paginated_data['total_results'],
            'base_url': url_for('movie_category', category=category)
        }
    )


@app.route('/people')
def people():
    """
    Displays the Popular People (Actors, Directors, Filmmakers) page
    with integrated real-time search and pagination.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    if q:
        data = search_people(query=q, language=tmdb_lang, page=page)
        base_url = url_for('people', q=q)
    else:
        data = get_popular_people(language=tmdb_lang, page=page, return_meta=True)
        base_url = url_for('people')

    people_list = data.get('people', [])
    pagination = {
        'page': data.get('page', 1),
        'total_pages': data.get('total_pages', 1),
        'total_results': data.get('total_results', len(people_list)),
        'base_url': base_url
    }

    return render_template('people.html', people=people_list, search_query=q, pagination=pagination)


@app.route('/person/<int:person_id>')
def person_detail(person_id):
    """
    Displays comprehensive details for an actor or director on-site,
    including biography, personal details, directed movies, and acting roles.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    person = get_person_details(person_id, language=tmdb_lang)
    if not person:
        return render_template('error.html', error_type='not_found', query=f'Person #{person_id}')

    return render_template('person_detail.html', person=person)


@app.route('/awards')
def awards():
    """
    Displays the Awards & Masterpieces Hall of Fame directory
    with category filters and live keyword search.
    """
    q = request.args.get('q', '').strip()
    category = request.args.get('category', 'all').strip().lower()
    sort = request.args.get('sort', 'popular').strip().lower()

    awards_list = get_all_awards(category=category, query=q, sort=sort)

    return render_template(
        'awards.html',
        awards=awards_list,
        active_category=category,
        search_query=q,
        active_sort=sort
    )


@app.route('/award/<string:slug>')
def award_detail(slug):
    """
    Displays dedicated award details on-site with celebrated winning/nominated
    masterpiece movies fetched directly from TMDb.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    award = get_award_by_slug(slug, language=tmdb_lang)
    if not award:
        return render_template('error.html', error_type='not_found', query=f'Award: {slug}')

    return render_template('award_detail.html', award=award)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Searches TMDb and returns a list of matching movies with pagination support.
    """
    if request.method == 'POST':
        query = request.form.get('movie_name', '').strip()
        page = 1
    else:
        query = request.args.get('q', '').strip() or request.args.get('movie_name', '').strip()
        page = request.args.get('page', 1, type=int)

    if page < 1:
        page = 1

    if not query:
        return redirect(url_for('index'))

    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    paginated_data = search_movies_paginated(query, language=tmdb_lang, page=page)
    movies = paginated_data['movies']

    if not movies and page == 1:
        return render_template('error.html', error_type='not_found', query=query)

    return render_template(
        'search_results.html',
        movies=movies,
        search_query=query,
        result_title=None,
        is_genre=False,
        pagination={
            'page': paginated_data['page'],
            'total_pages': paginated_data['total_pages'],
            'total_results': paginated_data['total_results'],
            'base_url': url_for('search', q=query)
        }
    )


@app.route('/genre/<int:genre_id>')
def genre_movies(genre_id):
    """
    Discovers and displays movies belonging to a specific genre with pagination.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    genres = get_genres(language=tmdb_lang)
    genre_name = next((g['name'] for g in genres if g['id'] == genre_id), f'Genre #{genre_id}')

    paginated_data = get_movies_by_genre_paginated(genre_id, language=tmdb_lang, page=page)
    movies = paginated_data['movies']

    if not movies and page == 1:
        return render_template('error.html', error_type='not_found', query=genre_name)

    return render_template(
        'search_results.html',
        movies=movies,
        search_query=genre_name,
        result_title=genre_name,
        is_genre=True,
        genre_id=genre_id,
        genres=genres,
        pagination={
            'page': paginated_data['page'],
            'total_pages': paginated_data['total_pages'],
            'total_results': paginated_data['total_results'],
            'base_url': url_for('genre_movies', genre_id=genre_id)
        }
    )


@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """
    Displays full details for a selected movie by its ID,
    including actors/cast, YouTube trailer, interactive Sentiment AI,
    TMDb community reviews, and similar movie recommendations.
    """
    current_lang = session.get('lang', DEFAULT_LANGUAGE)
    tmdb_lang = get_tmdb_language(current_lang)

    movie_info = get_movie_details_by_id(movie_id, language=tmdb_lang)

    if not movie_info:
        return render_template('error.html', error_type='not_found', query=f'Movie #{movie_id}')

    # Fetch similar movies & TMDb community reviews
    similar_movies = get_similar_movies(movie_id, language=tmdb_lang, limit=6)
    tmdb_reviews = get_movie_reviews_tmdb(movie_id, language=tmdb_lang, limit=4)

    # Check if movie is currently in user's watchlist
    in_watchlist = False
    if current_user.is_authenticated:
        try:
            in_watchlist = Watchlist.query.filter_by(
                user_id=current_user.id,
                movie_id=movie_id
            ).first() is not None
        except Exception:
            in_watchlist = False

    return render_template(
        'result.html',
        movie_info=movie_info,
        similar_movies=similar_movies,
        tmdb_reviews=tmdb_reviews,
        in_watchlist=in_watchlist
    )


@app.route('/analyze_sentiment', methods=['POST'])
def analyze_review():
    """
    AJAX / Form endpoint for real-time sentiment analysis.
    Saves analysis to ReviewHistory and notifies Telegram bot on notable reviews.
    """
    if request.is_json:
        data = request.get_json() or {}
        review_text = data.get('review_text') or data.get('review') or data.get('user_review', '')
        movie_title = data.get('movie_name') or data.get('movie_title', '')
        movie_id = data.get('movie_id')
    else:
        review_text = request.form.get('review_text') or request.form.get('user_review') or request.form.get('review', '')
        movie_title = request.form.get('movie_name') or request.form.get('movie_title', '')
        movie_id = request.form.get('movie_id')

    result = analyze_sentiment(review_text)

    # Save to ReviewHistory in DB
    saved_review_id = None
    if review_text and review_text.strip():
        try:
            history_entry = ReviewHistory(
                user_id=current_user.id if current_user.is_authenticated else None,
                movie_id=int(movie_id) if movie_id and str(movie_id).isdigit() else None,
                movie_title=movie_title or None,
                review_text=review_text.strip(),
                sentiment=result.get('sentiment', 'neutral'),
                polarity=result.get('polarity', 0.0),
                subjectivity=result.get('subjectivity', 0.0),
                positive_pct=result.get('positive_pct', 0.0),
                neutral_pct=result.get('neutral_pct', 0.0),
                negative_pct=result.get('negative_pct', 0.0),
                tone_description=result.get('tone_description', ''),
                detected_lang_name=result.get('detected_lang_name', '')
            )
            db.session.add(history_entry)
            db.session.commit()
            saved_review_id = history_entry.id

            # Trigger Telegram alert for analyzed reviews (positive, negative, and neutral)
            username = current_user.username if current_user.is_authenticated else "Guest User"
            sentiment = result.get('sentiment', 'neutral').lower()
            if sentiment == 'neutral':
                telegram_bot.notify_neutral_alert(
                    movie_title=movie_title,
                    review_text=review_text,
                    sentiment_data=result,
                    username=username
                )
            else:
                telegram_bot.notify_sentiment_alert(
                    movie_title=movie_title,
                    review_text=review_text,
                    sentiment_data=result,
                    username=username
                )
        except Exception as e:
            db.session.rollback()
            app.logger.warning(f"Failed to record review history: {e}")

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'data': result,
            'saved_id': saved_review_id,
            **result
        })

    if movie_id:
        return redirect(url_for('movie_detail', movie_id=movie_id))
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_type='404'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_type='500'), 500
