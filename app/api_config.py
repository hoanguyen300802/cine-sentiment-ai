"""
TMDb API Service Client
Handles movie search, detailed metadata, cast & crew credits, and video trailers.
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


def get_movie_info(movie_name, language='en-US'):
    """
    Searches for a movie by name and fetches rich details, cast, and trailers from TMDb.
    
    Parameters:
        movie_name (str): Search term for movie title
        language (str): TMDb ISO language code (e.g., 'en-US', 'vi-VN', 'zh-CN')
        
    Returns:
        dict: Complete movie details dictionary or None if not found
    """
    if not movie_name or not movie_name.strip():
        return None

    api_key = os.getenv('TMDB_API_KEY', DEFAULT_API_KEY)
    
    try:
        # Step 1: Search movie by query
        search_url = f'{BASE_URL}/search/movie'
        search_params = {
            'api_key': api_key,
            'query': movie_name.strip(),
            'language': language,
            'include_adult': 'false'
        }
        
        response = requests.get(search_url, params=search_params, timeout=8)
        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get('results', [])
        
        if not results:
            return None

        first_movie = results[0]
        movie_id = first_movie.get('id')

        # Step 2: Fetch full details (runtime, genres, tagline)
        details_url = f'{BASE_URL}/movie/{movie_id}'
        details_params = {
            'api_key': api_key,
            'language': language
        }
        
        details_resp = requests.get(details_url, params=details_params, timeout=8)
        if details_resp.status_code == 200:
            movie_details = details_resp.json()
        else:
            movie_details = first_movie

        # Step 3: Fetch Cast & Credits (/credits)
        credits_url = f'{BASE_URL}/movie/{movie_id}/credits'
        credits_resp = requests.get(credits_url, params={'api_key': api_key, 'language': language}, timeout=8)
        cast_list = []
        if credits_resp.status_code == 200:
            raw_cast = credits_resp.json().get('cast', [])
            for person in raw_cast[:12]:  # Top 12 main actors
                profile_path = person.get('profile_path')
                cast_list.append({
                    'id': person.get('id'),
                    'name': person.get('name', 'Unknown Actor'),
                    'character': person.get('character', 'Character'),
                    'profile_url': f'{PROFILE_BASE_URL}{profile_path}' if profile_path else None
                })

        # Step 4: Fetch Official Trailers & Videos (/videos)
        videos_url = f'{BASE_URL}/movie/{movie_id}/videos'
        videos_resp = requests.get(videos_url, params={'api_key': api_key, 'language': language}, timeout=8)
        raw_videos = []
        if videos_resp.status_code == 200:
            raw_videos = videos_resp.json().get('results', [])
            
        # Fallback to English trailers if localized query returned no videos
        if not raw_videos and language != 'en-US':
            fallback_resp = requests.get(videos_url, params={'api_key': api_key, 'language': 'en-US'}, timeout=8)
            if fallback_resp.status_code == 200:
                raw_videos = fallback_resp.json().get('results', [])

        trailer_key = None
        trailer_name = None
        # Prioritize YouTube Trailer or Teaser
        for v in raw_videos:
            if v.get('site') == 'YouTube' and v.get('type') in ['Trailer', 'Teaser']:
                trailer_key = v.get('key')
                trailer_name = v.get('name')
                if v.get('official'):  # Stop at first official trailer
                    break

        trailer_url = f'https://www.youtube.com/embed/{trailer_key}' if trailer_key else None

        # Extract General Metadata
        title = movie_details.get('title') or first_movie.get('title', 'Unknown Title')
        overview = movie_details.get('overview') or first_movie.get('overview', 'No overview available.')
        release_date = movie_details.get('release_date') or first_movie.get('release_date', 'N/A')
        rating = round(movie_details.get('vote_average', first_movie.get('vote_average', 0.0)), 1)
        vote_count = movie_details.get('vote_count', first_movie.get('vote_count', 0))
        popularity = round(movie_details.get('popularity', first_movie.get('popularity', 0.0)), 1)
        runtime = movie_details.get('runtime', None)
        tagline = movie_details.get('tagline', '')

        # Genres
        genres_data = movie_details.get('genres', [])
        genres = [g['name'] for g in genres_data if 'name' in g] if genres_data else []

        # Posters and Backdrops
        poster_path = movie_details.get('poster_path') or first_movie.get('poster_path')
        poster_url = f'{IMAGE_BASE_URL}{poster_path}' if poster_path else None

        backdrop_path = movie_details.get('backdrop_path') or first_movie.get('backdrop_path')
        backdrop_url = f'{BACKDROP_BASE_URL}{backdrop_path}' if backdrop_path else None

        tmdb_url = f'https://www.themoviedb.org/movie/{movie_id}'

        return {
            'id': movie_id,
            'title': title,
            'tagline': tagline,
            'overview': overview,
            'release_date': release_date,
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

    except (requests.RequestException, ValueError, KeyError):
        return None