"""
TMDb API Service Client
Handles movie search, genre exploration, movie categories (popular, now_playing, upcoming, top_rated),
popular people, detailed metadata, cast & crew credits, and video trailers.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# TMDb Configuration
DEFAULT_API_KEY = 'cf5fcc46b705439ea01d35de3e579877'
TMDB_API_KEY = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
PROFILE_BASE_URL = 'https://image.tmdb.org/t/p/w185'
BACKDROP_BASE_URL = 'https://image.tmdb.org/t/p/original'


def get_genres(language='en-US'):
    """Fetch all available movie genres from TMDb."""
    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/genre/movie/list'
    params = {'api_key': api_key, 'language': language}
    try:
        resp = requests.get(url, params=params, timeout=6)
        if resp.status_code == 200:
            return resp.json().get('genres', [])
    except Exception:
        pass
    return []


def search_movies(query, language='en-US', page=1):
    """
    Searches for movies matching a keyword query and returns a list of results.
    """
    if not query or not query.strip():
        return []

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    search_url = f'{BASE_URL}/search/movie'
    params = {
        'api_key': api_key,
        'query': query.strip(),
        'language': language,
        'include_adult': 'false',
        'page': page
    }

    try:
        resp = requests.get(search_url, params=params, timeout=8)
        if resp.status_code != 200:
            return []

        raw_results = resp.json().get('results', [])
        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })
        return movies
    except Exception:
        return []


def search_movies_paginated(query, language='en-US', page=1):
    """
    Searches TMDb and returns results with pagination metadata.
    """
    if not query or not query.strip():
        return {'movies': [], 'page': 1, 'total_pages': 1, 'total_results': 0}

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    search_url = f'{BASE_URL}/search/movie'
    params = {
        'api_key': api_key,
        'query': query.strip(),
        'language': language,
        'include_adult': 'false',
        'page': page
    }

    try:
        resp = requests.get(search_url, params=params, timeout=8)
        if resp.status_code != 200:
            return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}

        data = resp.json()
        raw_results = data.get('results', [])
        total_pages = min(data.get('total_pages', 1), 500)
        total_results = data.get('total_results', len(raw_results))

        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })

        return {
            'movies': movies,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_results
        }
    except Exception:
        return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}



def get_movies_by_category(category='popular', language='en-US', page=1):
    """
    Fetch movies by category: popular, now_playing, upcoming, top_rated.
    """
    valid_categories = ['popular', 'now_playing', 'upcoming', 'top_rated']
    if category not in valid_categories:
        category = 'popular'

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/movie/{category}'
    params = {
        'api_key': api_key,
        'language': language,
        'page': page
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return []

        raw_results = resp.json().get('results', [])
        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })
        return movies
    except Exception:
        return []


def get_movies_by_genre(genre_id, language='en-US', page=1):
    """Fetch top movies filtered by a specific genre ID."""
    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': api_key,
        'with_genres': str(genre_id),
        'language': language,
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'page': page
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return []

        raw_results = resp.json().get('results', [])
        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })
        return movies
    except Exception:
        return []


def get_popular_movies(language='en-US', page=1):
    """Fetch currently trending and popular movies for the home page."""
    return get_movies_by_category('popular', language=language, page=page)[:12]


def get_popular_people(language='en-US', page=1, return_meta=False):
    """
    Fetch list of popular actors and directors from TMDb.
    """
    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/person/popular'
    params = {
        'api_key': api_key,
        'language': language,
        'page': page
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return {'people': [], 'page': page, 'total_pages': 1, 'total_results': 0} if return_meta else []

        data = resp.json()
        raw_people = data.get('results', [])
        total_pages = min(data.get('total_pages', 1), 50)
        total_results = data.get('total_results', len(raw_people))

        people = []
        for p in raw_people:
            profile_path = p.get('profile_path')
            known_for_raw = p.get('known_for', [])
            known_titles = []
            for k in known_for_raw:
                title = k.get('title') or k.get('name')
                if title:
                    known_titles.append(title)

            people.append({
                'id': p.get('id'),
                'name': p.get('name', 'Unknown Person'),
                'department': p.get('known_for_department', 'Acting'),
                'popularity': round(p.get('popularity', 0.0), 1),
                'profile_url': f'{PROFILE_BASE_URL}{profile_path}' if profile_path else None,
                'known_for_titles': known_titles[:3]
            })

        if return_meta:
            return {
                'people': people,
                'page': page,
                'total_pages': total_pages,
                'total_results': total_results
            }
        return people
    except Exception:
        return {'people': [], 'page': page, 'total_pages': 1, 'total_results': 0} if return_meta else []


def search_people(query, language='en-US', page=1):
    """
    Search actors, directors, and filmmakers on TMDb by keyword with pagination.
    """
    if not query:
        return {'people': [], 'page': 1, 'total_pages': 1, 'total_results': 0}

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/search/person'
    params = {
        'api_key': api_key,
        'query': query,
        'language': language,
        'page': page,
        'include_adult': 'false'
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return {'people': [], 'page': page, 'total_pages': 1, 'total_results': 0}

        data = resp.json()
        raw_people = data.get('results', [])
        total_pages = min(data.get('total_pages', 1), 50)
        total_results = data.get('total_results', len(raw_people))

        people = []
        for p in raw_people:
            profile_path = p.get('profile_path')
            known_for_raw = p.get('known_for', [])
            known_titles = []
            for k in known_for_raw:
                title = k.get('title') or k.get('name')
                if title:
                    known_titles.append(title)

            people.append({
                'id': p.get('id'),
                'name': p.get('name', 'Unknown Person'),
                'department': p.get('known_for_department', 'Acting'),
                'popularity': round(p.get('popularity', 0.0), 1),
                'profile_url': f'{PROFILE_BASE_URL}{profile_path}' if profile_path else None,
                'known_for_titles': known_titles[:3]
            })

        return {
            'people': people,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_results
        }
    except Exception:
        return {'people': [], 'page': page, 'total_pages': 1, 'total_results': 0}


def get_person_details(person_id, language='en-US'):
    """
    Fetches comprehensive person details including biography, birthday,
    place of birth, department, directed movies, and acted roles.
    """
    if not person_id:
        return None

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/person/{person_id}'
    params = {
        'api_key': api_key,
        'language': language,
        'append_to_response': 'movie_credits'
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return None

        p = resp.json()
        biography = p.get('biography') or ''

        # If biography is empty in localized language, try English fallback
        if not biography.strip() and language != 'en-US':
            try:
                en_resp = requests.get(url, params={'api_key': api_key, 'language': 'en-US'}, timeout=5)
                if en_resp.status_code == 200:
                    biography = en_resp.json().get('biography') or ''
            except Exception:
                pass

        profile_path = p.get('profile_path')
        credits = p.get('movie_credits', {})

        # Parse directed movies (crew where job == 'Director')
        raw_crew = credits.get('crew', [])
        directed_dict = {}
        for m in raw_crew:
            if m.get('job') == 'Director':
                m_id = m.get('id')
                if m_id not in directed_dict:
                    poster_path = m.get('poster_path')
                    directed_dict[m_id] = {
                        'id': m_id,
                        'title': m.get('title') or m.get('original_title', 'Unknown'),
                        'release_date': m.get('release_date') or 'N/A',
                        'year': (m.get('release_date') or '')[:4] or 'N/A',
                        'rating': round(m.get('vote_average', 0.0), 1),
                        'vote_count': m.get('vote_count', 0),
                        'popularity': round(m.get('popularity', 0.0), 1),
                        'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                        'overview': m.get('overview') or '',
                        'job': 'Director'
                    }

        directed_movies = sorted(
            directed_dict.values(),
            key=lambda x: (x.get('popularity', 0), x.get('vote_count', 0)),
            reverse=True
        )

        # Parse acted movies (cast)
        raw_cast = credits.get('cast', [])
        acted_dict = {}
        for m in raw_cast:
            m_id = m.get('id')
            if m_id not in acted_dict:
                poster_path = m.get('poster_path')
                acted_dict[m_id] = {
                    'id': m_id,
                    'title': m.get('title') or m.get('original_title', 'Unknown'),
                    'character': m.get('character') or '',
                    'release_date': m.get('release_date') or 'N/A',
                    'year': (m.get('release_date') or '')[:4] or 'N/A',
                    'rating': round(m.get('vote_average', 0.0), 1),
                    'vote_count': m.get('vote_count', 0),
                    'popularity': round(m.get('popularity', 0.0), 1),
                    'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                    'overview': m.get('overview') or ''
                }

        acted_movies = sorted(
            acted_dict.values(),
            key=lambda x: (x.get('popularity', 0), x.get('vote_count', 0)),
            reverse=True
        )

        return {
            'id': p.get('id'),
            'name': p.get('name') or 'Unknown Person',
            'biography': biography,
            'birthday': p.get('birthday'),
            'deathday': p.get('deathday'),
            'place_of_birth': p.get('place_of_birth'),
            'department': p.get('known_for_department', 'Acting'),
            'popularity': round(p.get('popularity', 0.0), 1),
            'profile_url': f'{PROFILE_BASE_URL}{profile_path}' if profile_path else None,
            'directed_movies': directed_movies,
            'acted_movies': acted_movies,
            'tmdb_url': f'https://www.themoviedb.org/person/{person_id}'
        }
    except Exception:
        return None



def get_movie_details_by_id(movie_id, language='en-US'):
    """
    Fetches full movie metadata, cast members, and trailers by movie ID.
    """
    if not movie_id:
        return None

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)

    try:
        # Step 1: Main Details
        details_url = f'{BASE_URL}/movie/{movie_id}'
        details_params = {'api_key': api_key, 'language': language}
        details_resp = requests.get(details_url, params=details_params, timeout=8)
        if details_resp.status_code != 200:
            return None

        movie_details = details_resp.json()

        # Step 2: Cast & Credits
        credits_url = f'{BASE_URL}/movie/{movie_id}/credits'
        credits_resp = requests.get(credits_url, params={'api_key': api_key, 'language': language}, timeout=8)
        cast_list = []
        if credits_resp.status_code == 200:
            raw_cast = credits_resp.json().get('cast', [])
            for person in raw_cast[:12]:
                profile_path = person.get('profile_path')
                cast_list.append({
                    'id': person.get('id'),
                    'name': person.get('name', 'Unknown Actor'),
                    'character': person.get('character', 'Character'),
                    'profile_url': f'{PROFILE_BASE_URL}{profile_path}' if profile_path else None
                })

        # Step 3: Official Trailers
        videos_url = f'{BASE_URL}/movie/{movie_id}/videos'
        videos_resp = requests.get(videos_url, params={'api_key': api_key, 'language': language}, timeout=8)
        raw_videos = []
        if videos_resp.status_code == 200:
            raw_videos = videos_resp.json().get('results', [])

        if not raw_videos and language != 'en-US':
            fallback_resp = requests.get(videos_url, params={'api_key': api_key, 'language': 'en-US'}, timeout=8)
            if fallback_resp.status_code == 200:
                raw_videos = fallback_resp.json().get('results', [])

        trailer_key = None
        trailer_name = None
        for v in raw_videos:
            if v.get('site') == 'YouTube' and v.get('type') in ['Trailer', 'Teaser']:
                trailer_key = v.get('key')
                trailer_name = v.get('name')
                if v.get('official'):
                    break

        trailer_url = f'https://www.youtube.com/embed/{trailer_key}' if trailer_key else None

        title = movie_details.get('title') or 'Unknown Title'
        overview = movie_details.get('overview') or 'No overview available.'
        release_date = movie_details.get('release_date') or 'N/A'
        rating = round(movie_details.get('vote_average', 0.0), 1)
        vote_count = movie_details.get('vote_count', 0)
        popularity = round(movie_details.get('popularity', 0.0), 1)
        runtime = movie_details.get('runtime', None)
        tagline = movie_details.get('tagline', '')

        genres_data = movie_details.get('genres', [])
        genres = [g['name'] for g in genres_data if 'name' in g] if genres_data else []

        poster_path = movie_details.get('poster_path')
        poster_url = f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None

        backdrop_path = movie_details.get('backdrop_path')
        backdrop_url = f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None

        tmdb_url = f'https://www.themoviedb.org/movie/{movie_id}'

        return {
            'id': movie_id,
            'title': title,
            'tagline': tagline,
            'overview': overview,
            'release_date': release_date,
            'year': release_date[:4] if release_date != 'N/A' else 'N/A',
            'rating': rating,
            'vote_count': vote_count,
            'popularity': popularity,
            'runtime': runtime,
            'genres': genres,
            'poster_url': poster_url,
            'backdrop_url': backdrop_url,
            'tmdb_url': tmdb_url,
            'cast': cast_list,
            'trailer_key': trailer_key,
            'trailer_name': trailer_name,
            'trailer_url': trailer_url
        }

    except Exception:
        return None


def get_movie_info(movie_name, language='en-US'):
    """
    Backwards-compatible helper: searches for a movie name and returns details of first match.
    """
    movies = search_movies(movie_name, language=language)
    if movies:
        return get_movie_details_by_id(movies[0]['id'], language=language)
    return None


def get_movies_by_category_paginated(category='popular', language='en-US', page=1):
    """
    Fetch movies by category with full pagination metadata.
    """
    valid_categories = ['popular', 'now_playing', 'upcoming', 'top_rated']
    if category not in valid_categories:
        category = 'popular'

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/movie/{category}'
    params = {'api_key': api_key, 'language': language, 'page': page}

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}

        data = resp.json()
        raw_results = data.get('results', [])
        total_pages = min(data.get('total_pages', 1), 500)
        total_results = data.get('total_results', len(raw_results))

        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })
        return {
            'movies': movies,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_results
        }
    except Exception:
        return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}


def get_movies_by_genre_paginated(genre_id, language='en-US', page=1):
    """
    Fetch movies by genre with pagination metadata.
    """
    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': api_key,
        'with_genres': str(genre_id),
        'language': language,
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'page': page
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code != 200:
            return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}

        data = resp.json()
        raw_results = data.get('results', [])
        total_pages = min(data.get('total_pages', 1), 500)
        total_results = data.get('total_results', len(raw_results))

        movies = []
        for m in raw_results:
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            movies.append({
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or 'No overview available.',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'popularity': round(m.get('popularity', 0.0), 1),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            })
        return {
            'movies': movies,
            'page': page,
            'total_pages': total_pages,
            'total_results': total_results
        }
    except Exception:
        return {'movies': [], 'page': page, 'total_pages': 1, 'total_results': 0}


def get_similar_movies(movie_id, language='en-US', limit=6):
    """
    Fetches recommended or similar movies for a given movie ID.
    """
    if not movie_id:
        return []

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    for endpoint in ['recommendations', 'similar']:
        url = f'{BASE_URL}/movie/{movie_id}/{endpoint}'
        try:
            resp = requests.get(url, params={'api_key': api_key, 'language': language}, timeout=6)
            if resp.status_code == 200:
                raw = resp.json().get('results', [])
                if raw:
                    movies = []
                    for m in raw[:limit]:
                        poster_path = m.get('poster_path')
                        backdrop_path = m.get('backdrop_path')
                        movies.append({
                            'id': m.get('id'),
                            'title': m.get('title') or m.get('original_title', 'Unknown'),
                            'overview': m.get('overview', ''),
                            'year': (m.get('release_date') or '')[:4] or 'N/A',
                            'rating': round(m.get('vote_average', 0.0), 1),
                            'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                            'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
                        })
                    return movies
        except Exception:
            pass
    return []


def get_movie_reviews_tmdb(movie_id, language='en-US', limit=4):
    """
    Fetches community reviews for a movie from TMDb.
    """
    if not movie_id:
        return []

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    url = f'{BASE_URL}/movie/{movie_id}/reviews'

    try:
        resp = requests.get(url, params={'api_key': api_key, 'language': language}, timeout=6)
        if resp.status_code == 200:
            raw = resp.json().get('results', [])
            reviews = []
            for r in raw[:limit]:
                author = r.get('author') or 'Anonymous Reviewer'
                content = r.get('content') or ''
                created_at = (r.get('created_at') or '')[:10]
                author_details = r.get('author_details', {})
                user_rating = author_details.get('rating')
                avatar_path = author_details.get('avatar_path')
                avatar_url = None
                if avatar_path:
                    if avatar_path.startswith('/http'):
                        avatar_url = avatar_path[1:]
                    elif avatar_path.startswith('http'):
                        avatar_url = avatar_path
                    else:
                        avatar_url = f'{IMAGE_BASE_URL}{avatar_path}'

                short_content = (content[:260] + '...') if len(content) > 260 else content

                reviews.append({
                    'id': r.get('id'),
                    'author': author,
                    'content': content,
                    'short_content': short_content,
                    'created_at': created_at,
                    'rating': user_rating,
                    'avatar_url': avatar_url,
                    'url': r.get('url')
                })
            return reviews
    except Exception:
        pass
    return []


def get_movie_card(movie_id, language='en-US'):
    """
    Lightweight fetch of basic movie card metadata (title, poster, rating, year, overview).
    """
    if not movie_id:
        return None

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    try:
        url = f'{BASE_URL}/movie/{movie_id}'
        resp = requests.get(url, params={'api_key': api_key, 'language': language}, timeout=6)
        if resp.status_code == 200:
            m = resp.json()
            poster_path = m.get('poster_path')
            backdrop_path = m.get('backdrop_path')
            return {
                'id': m.get('id'),
                'title': m.get('title') or m.get('original_title', 'Unknown'),
                'overview': m.get('overview') or '',
                'release_date': m.get('release_date') or 'N/A',
                'year': (m.get('release_date') or '')[:4] or 'N/A',
                'rating': round(m.get('vote_average', 0.0), 1),
                'vote_count': m.get('vote_count', 0),
                'poster_url': f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None,
                'backdrop_url': f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None,
            }
    except Exception:
        pass
    return None


def get_award_by_slug(slug, language='en-US'):
    """
    Retrieves award details from AWARDS_CATALOG and fetches live TMDb data
    for celebrated winning/nominated movies.
    """
    from app.awards_data import get_award_by_slug_data
    award = get_award_by_slug_data(slug)
    if not award:
        return None

    award_data = dict(award)
    movie_ids = award.get('notable_movie_ids', [])
    movies = []
    for m_id in movie_ids:
        card = get_movie_card(m_id, language=language)
        if card:
            movies.append(card)

    award_data['movies'] = movies
    return award_data