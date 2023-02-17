from django.http import JsonResponse
from moviedb.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from graphMovieDB.settings import TMDB_API_KEY, TMDB_API_URL
from datetime import datetime
from moviedb.cypher_queries import movieQuery, personQuery


@csrf_exempt
def getMovie(request):
    if request.method == 'GET':
        title = request.GET.get('title', '')

        movie = Movie.nodes.first_or_none(title=title)
        if movie is None:
            movie = _findMovieInApi(title)

        if movie is None:
            response = {
                "message": "No movie"
            }
        else:
            nodes, links = movieQuery(movie.movie_id)
            response = {
                "movie": movie.__properties__,
                "nodes": nodes,
                "links": links
            }

        return JsonResponse(response, safe=False)


@csrf_exempt
def getPerson(request):
    if request.method == 'GET':
        name = request.GET.get('name', '')

        person = Person.nodes.first_or_none(name=name)

        if person is None:
            person = _findPersonInApi(name)

        if person is None:
            response = {
                "message": "No person"
            }
        else:
            nodes, links = personQuery(person.person_id)
            response = {
                "person": person.__properties__,
                "nodes": nodes,
                "links": links
            }
        return JsonResponse(response, safe=False)


def _findMovieInApi(title):
    query_request = requests.get(TMDB_API_URL + 'search/movie', params={"api_key": TMDB_API_KEY, "query": title})
    if query_request.status_code != 200 or len(query_request.json()['results']) == 0:
        return None

    movie_id = query_request.json()['results'][0]["id"]
    movie_title = query_request.json()['results'][0]["title"]
    potential_movie = Movie.nodes.first_or_none(title=movie_title)
    if potential_movie is not None:
        return potential_movie

    movie_request = requests.get(TMDB_API_URL + 'movie/' + str(movie_id), params={"api_key": TMDB_API_KEY})
    if movie_request.status_code != 200:
        return None

    movie_json = movie_request.json()

    movie = Movie(movie_id=str(movie_json["id"]),
                  imdb_id=movie_json["imdb_id"],
                  title=movie_json["title"],
                  tagline=movie_json["tagline"],
                  overview=movie_json["overview"],
                  budget=movie_json["budget"],
                  revenue=movie_json["revenue"],
                  release_date=datetime.strptime(movie_json["release_date"], '%Y-%m-%d') if movie_json[
                                                                                                "release_date"] is not None else None,
                  vote_avg=movie_json["vote_average"],
                  vote_count=movie_json["vote_count"])
    movie = movie.save()

    genres_json = movie_json["genres"]
    if genres_json is not None and len(genres_json) > 0:
        genres = []
        for g in genres_json:
            genres.append(Genre(genre_id=str(g["id"]), name=g["name"]))
        genres = _addGenresIfNeeded(genres)

        for genre in genres:
            movie.genres.connect(genre)
        movie = movie.save()

    actors, directors = _findActorsAndDirectorsForMovie(movie.movie_id)

    for actor in actors:
        movie.actors.connect(actor)

    for director in directors:
        movie.directed_by.connect(director)

    return movie


def _findPersonInApi(name):
    query_request = requests.get(TMDB_API_URL + 'search/person', params={"api_key": TMDB_API_KEY, "query": name})
    if query_request.status_code != 200 or len(query_request.json()['results']) == 0:
        return None

    person_id = query_request.json()['results'][0]["id"]
    person_name = query_request.json()['results'][0]["name"]
    potential_person = Person.nodes.first_or_none(name=person_name)
    if potential_person is not None:
        return potential_person

    return _addPersonById(person_id)


def _addPersonById(person_id):
    person_request = requests.get(TMDB_API_URL + 'person/' + str(person_id), params={"api_key": TMDB_API_KEY})
    if person_request.status_code != 200:
        return None

    person_json = person_request.json()

    person = Person(person_id=str(person_json["id"]),
                    imdb_id=person_json["imdb_id"],
                    name=person_json["name"],
                    birthday=datetime.strptime(person_json["birthday"], '%Y-%m-%d') if person_json[
                                                                                           "birthday"] is not None else None,
                    deathday=datetime.strptime(person_json["deathday"], '%Y-%m-%d') if person_json[
                                                                                           "deathday"] is not None else None,
                    biography=person_json["biography"])
    person = person.save()
    return person


def _addGenresIfNeeded(genres):
    if genres is None or len(genres) == 0:
        return []

    new_genres = []

    for genre in genres:
        db_genre = Genre.nodes.first_or_none(genre_id=genre.genre_id)
        if db_genre is not None:
            new_genres.append(db_genre)
        else:
            g = genre.save()
            new_genres.append(g)

    return new_genres


def _findActorsAndDirectorsForMovie(movie_id):
    credit_request = requests.get(TMDB_API_URL + 'movie/' + str(movie_id) + '/credits',
                                  params={"api_key": TMDB_API_KEY})
    if credit_request.status_code != 200:
        return [], []

    cast = credit_request.json()['cast']
    crew = credit_request.json()['crew']

    final_cast = []
    directors = []

    for person in cast:
        db_person = Person.nodes.first_or_none(person_id=person['id'])
        if db_person is not None:
            final_cast.append(db_person)
        else:
            final_cast.append(_addPersonById(person['id']))

    for person in crew:
        if person['job'] == "Director":
            db_person = Person.nodes.first_or_none(person_id=person['id'])
            if db_person is not None:
                directors.append(db_person)
            else:
                directors.append(_addPersonById(person['id']))

    return final_cast, directors

