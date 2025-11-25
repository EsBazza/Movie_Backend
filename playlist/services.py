import os
from typing import Optional, Tuple, List

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Movie


class TMDBError(Exception):
    pass


def _get_tmdb_config():
    api_key = getattr(settings, "TMDB_API_KEY", None) or os.environ.get("TMDB_API_KEY")
    base = getattr(settings, "TMDB_BASE_URL", None) or os.environ.get("TMDB_BASE_URL")
    image_base = getattr(settings, "TMDB_IMAGE_BASE", None) or os.environ.get("TMDB_IMAGE_BASE")
    if not api_key:
        raise ImproperlyConfigured("TMDB_API_KEY is not configured in settings or environment")
    if not base:
        base = "https://api.themoviedb.org/3"
    if not image_base:
        image_base = "https://image.tmdb.org/t/p/w500"
    return api_key, base.rstrip("/"), image_base.rstrip("/")


def search_tmdb(query: str, page: int = 1) -> dict:
    """Search TMDB for movies (returns parsed JSON).

    The endpoint is configurable via `TMDB_BASE_URL` in settings.
    """
    api_key, base, _ = _get_tmdb_config()
    url = f"{base}/search/movie"
    params = {"api_key": api_key, "query": query, "page": page}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_tmdb_movie_details(tmdb_id: int) -> dict:
    """Fetch the TMDB movie detail (including videos).

    Uses settings.TMDB_BASE_URL and APPENDS videos by default.
    """
    api_key, base, _ = _get_tmdb_config()
    url = f"{base}/movie/{tmdb_id}"
    params = {"api_key": api_key, "append_to_response": "videos"}
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 404:
        raise TMDBError(f"Movie {tmdb_id} not found")
    resp.raise_for_status()
    return resp.json()


def get_or_create_movie_from_tmdb(tmdb_id: int) -> Tuple[Movie, bool]:
    """Get or create a local Movie by tmdb_id.

    Returns (movie, created). If created is True, we fetched from TMDB.
    If the movie already exists locally, we return it without hitting TMDB.
    """
    # First check if we already have this movie cached locally
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
        return movie, False
    except Movie.DoesNotExist:
        pass

    # Fetch from TMDB
    data = get_tmdb_movie_details(tmdb_id)

    # Extract youtube_id from videos
    youtube_id = None
    videos = data.get("videos", {}).get("results", [])
    for v in videos:
        if v.get("site", "").lower() == "youtube" and v.get("key"):
            youtube_id = v.get("key")
            break

    # Build poster URL
    poster_path = data.get("poster_path")
    poster_url = None
    if poster_path:
        _, _, image_base = _get_tmdb_config()
        poster_url = f"{image_base}{poster_path}"

    # Parse release_year from release_date (e.g., "2010-07-15" -> 2010)
    release_year = None
    release_date = data.get("release_date") or ""
    if release_date:
        try:
            release_year = int(release_date.split("-")[0])
        except (ValueError, IndexError):
            release_year = None

    # Create the movie
    movie = Movie.objects.create(
        tmdb_id=tmdb_id,
        title=data.get("title") or data.get("original_title") or "",
        poster_url=poster_url,
        description=data.get("overview") or "",
        release_year=release_year,
        youtube_id=youtube_id,
    )

    return movie, True
