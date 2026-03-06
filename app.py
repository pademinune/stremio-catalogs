
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_caching import Cache
import tmdb
from dotenv import load_dotenv
import os
import math
import threading

CATALOG_SIZE = 40

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
CRON_SECRET = os.getenv("CRON_SECRET")

MANIFEST = {
    "id": "movie.genre.catalogs",
    "name": "Stremio Catalogs",
    "description": "Get more catalogs.",
    "version": "1.2.0",
    "resources": ["catalog"],
    "types": ["movie"],
    "catalogs": [{"type": "movie", "id": "action_movies", "name": "Action", "extra": [{"name": "skip"}]},
                 {"type": "movie", "id": "adventure_movies", "name": "Adventure", "extra": [{"name": "skip"}]},
                 {"type": "movie", "id": "comedy_movies", "name": "Comedy", "extra": [{"name": "skip"}]},
                 {"type": "movie", "id": "drama_movies", "name": "Drama", "extra": [{"name": "skip"}]},
                 {"type": "movie", "id": "fantasy_movies", "name": "Fantasy", "extra": [{"name": "skip"}]},
                 {"type": "movie", "id": "horror_movies", "name": "Horror", "extra": [{"name": "skip"}]},
                #  {"type": "movie", "id": "sub_100_minutes", "name": "Movies Under 100 minutes", "extra": [{"name": "skip"}]},
                #  {"type": "movie", "id": "documentaries", "name": "Documentaries", "extra": [{"name": "skip"}]},
                #  {"type": "movie", "id": "random_movie", "name": "Random Movie"}
                 ],
    "logo": f"{BASE_URL}/static/img/favicon.png"
}

ID_TO_GENRE = {
    "action_movies": "Action",
    "adventure_movies": "Adventure",
    "comedy_movies": "Comedy",
    "drama_movies": "Drama",
    "fantasy_movies": "Fantasy",
    "horror_movies": "Horror",
    # "documentaries": "Documentary",
}

app = Flask(__name__)
CORS(app)

app.config.from_mapping({
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL"),
    "CACHE_DEFAULT_TIMEOUT": 86400  # 24-hour default
})

cache = Cache(app)

def get_page_num(skip: int) -> int:
    """find page st 20 * page >= skip and page is minimal"""
    return math.ceil(skip / 20) + 1

def get_cache_key(catalog_id: str, page: int = 1) -> str:
    return f"{catalog_id}_page={page}"

def get_skip_from_args(args: str | None) -> int:
    skip = 0
    if args and 'skip=' in args:
        try:
            skip = int(args.split('=')[1])
        except ValueError:
            skip = 0
    return skip

def fetch_movie_genre(catalog_id: str, page: int = 0):
    genre = ID_TO_GENRE[catalog_id]
    
    movies = tmdb.get_movies(genre, CATALOG_SIZE, start_page=page)
    metas = [movie.to_dict() for movie in movies]
    response = {"metas": metas}
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/manifest.json")
def manifest():
    return MANIFEST

@app.route('/catalog/movie/random_movie.json')
def random_movie():
    movie = tmdb.get_random_movie()
    return {"metas": [movie.to_dict()]}

@app.route('/catalog/movie/sub_100_minutes/<path:args>.json')
@app.route("/catalog/movie/sub_100_minutes.json")
def sub_100_minutes(args=None):
    skip = 0
    if args and 'skip=' in args:
        try:
            skip = int(args.split('=')[1])
        except ValueError:
            skip = 0

    page = skip // 20 + 1
    if (skip % 20 != 0): # it was rounded down, so add 1
        page += 1
    
    movies = tmdb.get_movies_filtered({"with_runtime.lte": 100, "with_runtime.gte": 60},
                                       CATALOG_SIZE, start_page=page)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/<catalog_id>/<path:args>.json')
@app.route('/catalog/movie/<catalog_id>.json')
def movie_catalog(catalog_id, args = None):    
    skip = get_skip_from_args(args)
    page = get_page_num(skip=skip)

    cache_key = get_cache_key(catalog_id, page)
    cached = cache.get(cache_key)
    if (cached):
        return cached

    response = fetch_movie_genre(catalog_id, page)

    cache.set(cache_key, response)
    return response

@app.route("/cache/refresh", methods=["POST"])
def refresh_cache_endpoint():
    token = request.headers.get("X-Cron-Secret")
    if token != CRON_SECRET:
        return "Unauthorized", 401
    
    thread = threading.Thread(target=refresh_cache)
    thread.start()
    return "Cache refresh started."

def refresh_cache():
    for catalog_id in ID_TO_GENRE.keys():
        response = fetch_movie_genre(catalog_id, page=1)
        cache_key = get_cache_key(catalog_id, page=1)
        cache.set(cache_key, response)

@app.route("/cache/reset", methods=["POST"])
@app.route("/cache/clear", methods=["POST"])
def clear_cache_endpoint():
    token = request.headers.get("X-Cron-Secret")
    if token != CRON_SECRET:
        return "Unauthorized", 401

    thread = threading.Thread(target=clear_cache)
    thread.start()
    return "Cache clear started."

def clear_cache():
    cache.clear()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)
