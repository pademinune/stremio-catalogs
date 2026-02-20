
import requests
import json
from dotenv import load_dotenv
import os
import random

load_dotenv()

TMDB_KEY = os.getenv("TMDB_KEY")
BASE_URL = os.getenv("BASE_URL")

GENRE_IDS = {"Action": 28, "Adventure": 12, "Animation": 16,
             "Comedy": 35, "Crime": 80, "Documentary": 99,
             "Drama": 18, "Family": 10751, "Fantasy": 14,
             "History": 36, "Horror": 27, "Music": 10402,
             "Mystery": 9648, "Romance": 10749,
             "Science-Fiction": 878, "TV-Movie": 10770,
             "Thriller": 53, "War": 10752, "Western": 37,
             "Documentary": 99,
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

def is_valid_movie(movie) -> bool:
    return (movie["poster_path"] is not None) and (movie["id"] is not None)

def get_imdb_id(tmdb_id: int) -> str:
    query = f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={TMDB_KEY}"
    response = requests.get(query)
    response_dict = response.json()
    return response_dict["imdb_id"]

def get_poster_url(short_url: str) -> str:
    if (not short_url):
        return f"{BASE_URL}/static/img/poster_placeholder.png"
    return f"https://image.tmdb.org/t/p/w500{short_url}"

def get_movies(genre: str, amount: int = 20, start_page = 1) -> list[Movie]:
    genre_id = GENRE_IDS[genre]
    movies = []
    page_number = start_page

    while (len(movies) < amount):
        # query = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&sort_by=popularity.desc&page={page_number}&with_genres={genre_id}"
        url = "https://api.themoviedb.org/3/discover/movie"
        response = requests.get(url, params={"api_key": TMDB_KEY, "sort_by": "popularity.desc", 
                                             "page": page_number, "with_genres": genre_id})
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

def get_movies_filtered(filters: dict[str, str|int], amount: int = 20, start_page = 1) -> list[Movie]:
    movies = []
    page_number = start_page

    while (len(movies) < amount):
        # query = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&sort_by=popularity.desc&page={page_number}&with_genres={genre_id}"
        url = "https://api.themoviedb.org/3/discover/movie"
        response = requests.get(url, params=({"api_key": TMDB_KEY, "sort_by": "popularity.desc", 
                                             "page": page_number} | filters))
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

def get_random_movie() -> Movie:
    url = "https://api.themoviedb.org/3/discover/movie"
    page = random.randint(1, 25)
    response = requests.get(url, params={"api_key": TMDB_KEY, "sort_by": "popularity.desc", "page": page}).json()
    response_movies = response["results"]

    movie = random.choice(response_movies)
    if (not is_valid_movie(movie)):
        return get_random_movie()
    
    imdb_id = get_imdb_id(movie["id"])
    name = movie["title"]
    poster_url = get_poster_url(movie["poster_path"])

    return Movie(imdb_id, name, poster_url)


if __name__ == "__main__":
    # movies = get_movies("Horror", 10, 1)
    # print(len(movies))
    # print([movie.name for movie in movies])
    movie = get_random_movie()
    print(movie)
    # for movie in movies:
    #     print(movie)

