
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MANIFEST = {
    "id": "org.stremio.python_example",
    "name": "Movie Genre Catalogs",
    "description": "Get more catalogs.",
    "version": "1.1.0",
    "resources": ["catalog"],
    "types": ["movie"],
    "catalogs": [{"type": "movie", "id": "python_movies", "name": "Python Movies"}]
}

# MANIFEST = {
#     "id": "movie.trailers.justin",
#     "name": "Movie Trailers",
#     "description": "Watch movie trailers.",
#     "version": "1.1.0",
#     "resources": ["stream"],
#     "types": ["movie"],
#     "catalogs": [],
#     "idPrefixes": ["tt"],
# }

@app.route('/manifest.json')
def manifest():
    return MANIFEST

@app.route('/catalog/movie/python_movies.json')
def catalog():
    # This is the "row" content
    metas = [
        {
            "id": "tt0111161", # IMDb ID
            "type": "movie",
            "name": "The Shawshank Redemption",
            "poster": "https://images.metahub.space",
        }
    ]
    return {"metas": metas}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)
