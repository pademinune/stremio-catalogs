
from flask import Flask, render_template
from flask_cors import CORS
from flask_caching import Cache
import tmdb
from dotenv import load_dotenv
import os
import redis_cache

CATALOG_SIZE = 40

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

MANIFEST = {
    "id": "movie.genre.catalogs",
    "name": "Stremio Catalogs",
    "description": "Get more catalogs.",
    "version": "1.1.1",
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
    "documentaries": "Documentary",
}

app = Flask(__name__)
CORS(app)

app.config.from_mapping({
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL"),
    "CACHE_DEFAULT_TIMEOUT": 86400  # 24-hour default
})

cache = Cache(app)

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
@cache.cached()
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
    
    movies = tmdb.get_movies_filtered({"with_runtime.lte": 100, "with_runtime.gte": 60}, CATALOG_SIZE, start_page=page)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/<id>/<path:args>.json')
@app.route('/catalog/movie/<id>.json')
# @cache.cached()
def movie_catalog(id, args = None):
    cached = redis_cache.get_cache(id)
    if (cached):
        return cached

    genre = ID_TO_GENRE[id]

    skip = 0
    if args and 'skip=' in args:
        try:
            skip = int(args.split('=')[1])
        except ValueError:
            skip = 0

    page = skip // 20 + 1
    if (skip % 20 != 0): # it was rounded down, so add 1
        page += 1
    
    movies = tmdb.get_movies(genre, CATALOG_SIZE, start_page=page)
    metas = [movie.to_dict() for movie in movies]
    response = {"metas": metas}
    redis_cache.set_cache(id, response)
    return response


@app.route("/clear-cache")
def clear_cache():
    cache.clear()
    return "Cache cleared successfully!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)
