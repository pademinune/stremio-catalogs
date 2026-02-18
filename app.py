
from flask import Flask
from flask_cors import CORS
import tmdb
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

CATALOG_SIZE = 10

# load_dotenv()
# BASE_URL = os.getenv("BASE_URL")

MANIFEST = {
    "id": "movie.genre.catalogs",
    "name": "Movie Genre Catalogs",
    "description": "Get more catalogs.",
    "version": "1.0.0",
    "resources": ["catalog"],
    "types": ["movie"],
    "catalogs": [{"type": "movie", "id": "action_movies", "name": "Action Movies"},
                 {"type": "movie", "id": "adventure_movies", "name": "Adventure Movies"},
                 {"type": "movie", "id": "comedy_movies", "name": "Comedy Movies"},
                 {"type": "movie", "id": "drama_movies", "name": "Drama Movies"},
                 {"type": "movie", "id": "fantasy_movies", "name": "Fantasy Movies"},
                 {"type": "movie", "id": "horror_movies", "name": "Horror Movies"}
                 ],
    # "logo": f"{BASE_URL}/static/img/favicon.png"
}

@app.route('/manifest.json')
def manifest():
    return MANIFEST

@app.route('/catalog/movie/action_movies.json')
def action_catalog():
    movies = tmdb.get_movies("Action", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/adventure_movies.json')
def adventure_catalog():
    movies = tmdb.get_movies("Adventure", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/comedy_movies.json')
def comedy_catalog():
    movies = tmdb.get_movies("Comedy", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/drama_movies.json')
def drama_catalog():
    movies = tmdb.get_movies("Drama", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/fantasy_movies.json')
def fantasy_catalog():
    movies = tmdb.get_movies("Fantasy", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}

@app.route('/catalog/movie/horror_movies.json')
def horror_catalog():
    movies = tmdb.get_movies("Horror", CATALOG_SIZE)
    metas = [movie.to_dict() for movie in movies]
    return {"metas": metas}



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)
