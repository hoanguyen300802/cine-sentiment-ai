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


def search_movies(query, language='en-US'):
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
        'include_adult': 'false'
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


def get_popular_people(language='en-US', page=1):
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
            return []

        raw_people = resp.json().get('results', [])
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
        return people
    except Exception:
        return []


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