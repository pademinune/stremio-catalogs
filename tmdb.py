
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

TMDB_KEY = os.getenv("TMDB_KEY")
BASE_URL = os.getenv("BASE_URL")

GENRE_IDS = {"Action": 28, "Adventure": 12, "Animation": 16,
             "Comedy": 35, "Crime": 80, "Documentary": 99,
             "Drama": 18, "Family": 10751, "Fantasy": 14,
             "History": 36, "Horror": 27, "Music": 10402,
             "Mystery": 9648, "Romance": 10749,
             "Science-Fiction": 878, "TV-Movie": 10770,
             "Thriller": 53, "War": 10752, "Western": 37
             }


class Movie:
    def __init__(self, id: str, name: str, 
                 poster: str = "http://127.0.0.1:7000/static/img/9.jpg"):
        self.id = id # https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_KEY}
        self.name = name
        self.poster = poster # https://image.tmdb.org/t/p/w500/1E5baAaEse26fej7uHcjOgEE2t2.jpg

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "type": "movie", 
                "name": self.name, "poster": self.poster}
    
    def __str__(self) -> str:
        return str(self.to_dict())


def get_imdb_id(tmdb_id: int) -> str:
    query = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_KEY}"
    response = requests.get(query)
    response_dict = response.json()
    return response_dict["imdb_id"]

def get_poster_url(short_url: str) -> str:
    if (not short_url):
        return f"{BASE_URL}/static/img/poster_placeholder.png"
    return f"https://image.tmdb.org/t/p/w500{short_url}"

def get_movies(genre: str, amount: int = 20, start_page = 1):
    genre_id = GENRE_IDS[genre]
    movies = []
    page_number = start_page

    while (len(movies) < amount):
        query = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&language=en-US&sort_by=popularity.desc&page={page_number}&with_genres={genre_id}"
        response = requests.get(query)
        response_dict = response.json()
        response_movies = response_dict["results"]

        if (len(movies) + len(response_movies) <= amount):
            movies += response_movies
        else:
            movies += response_movies[0:(amount - len(movies))]
        page_number += 1
    
    movie_objects = []
    for movie in movies:
        imdb_id = get_imdb_id(movie["id"])
        name = movie["title"]
        poster_url = get_poster_url(movie["poster_path"])
        movie_objects.append(Movie(imdb_id, name, poster_url))

    return movie_objects


if __name__ == "__main__":
    movies = get_movies("Horror", 40, 3)
    print(len(movies))
    # for movie in movies:
    #     print(movie)

