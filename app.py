import sys
from flask import Flask, request, abort, jsonify
from werkzeug.exceptions import BadRequest, HTTPException, UnprocessableEntity, NotFound
from flask_cors import CORS
from auth import requires_auth
from datetime import datetime

from models import setup_db, Actors, Movies, MAX_ACTOR_NAME_LENGTH, MIN_ACTOR_NAME_LENGTH, MIN_ACTOR_AGE, MAX_ACTOR_AGE, \
    update, MAX_MOVIE_TITLE_LENGTH, MIN_MOVIE_TITLE_LENGTH


def create_app(test_config=None):
    app = Flask(__name__)
    if type(test_config) == dict:
        app.db = setup_db(app, **test_config)
    else:
        app.db = setup_db(app)


    CORS(
        app,
        origins='*',
        methods=['GET', 'POST', 'DELETE', 'PATCH'],
        allow_headers=['Authorization', 'Content-Type']
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH')
        return response

    @app.route('/actors')
    @requires_auth('get:actors')
    def get_actors():
        try:
            actors = Actors.query.order_by('id').all()
            response = {
                'actors': [actor.short() for actor in actors]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies():
        try:
            movies = Movies.query.order_by('id').all()
            response = {
                'movies': [movie.short() for movie in movies]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    def validate_actor(name=None, gender=None, age=None, updating=False):
        check_name = True if name is not None else False
        check_gender = True if gender is not None else False
        check_age = True if age is not None else False

        if not updating:
            if not isinstance(name, str) or not isinstance(gender, str) or not isinstance(age, int):
                raise UnprocessableEntity(
                    description=f'Name, gender and age must be the required types when creating an actor'
                )

        actor_data = {}

        if check_name:
            actor_data = {
                'name': name.strip()
            }

            actor_name_length = len(actor_data['name'])
            if actor_name_length < MIN_ACTOR_NAME_LENGTH or actor_name_length > MAX_ACTOR_NAME_LENGTH:
                raise UnprocessableEntity(
                    description=f'Actor name length must be between {MIN_ACTOR_NAME_LENGTH} and {MAX_ACTOR_NAME_LENGTH}'
                )

        if check_gender:
            actor_data['gender'] = gender.lower().strip()

            if actor_data['gender'] != 'm' and actor_data['gender'] != 'f':
                raise UnprocessableEntity(
                    description=f'Actor gender must be "m" or "f"'
                )

        if check_age:
            actor_data['age'] = age

            if not isinstance(actor_data['age'], int):
                raise UnprocessableEntity(
                    description=f'Actor age must an integer'
                )

            if not (actor_data['age'] > MIN_ACTOR_AGE or actor_data['age'] < MAX_ACTOR_AGE):
                raise UnprocessableEntity(
                    description=f'Actor age greater than {MIN_ACTOR_AGE} and less than {MAX_ACTOR_AGE}'
                )

        return actor_data

    def validate_movie(title=None, release_date=None, updating=False):
        check_title = True if title is not None else False
        check_release_date = True if release_date is not None else False

        if not updating:
            if not isinstance(title, str) or not isinstance(release_date, int):
                raise UnprocessableEntity(
                    description=f'Title and release date must be of the required types when creating a movie'
                )

        movie_data = {}

        if check_title:
            movie_data = {
                'title': title.strip()
            }

            movie_title_length = len(movie_data['title'])
            if movie_title_length < MIN_MOVIE_TITLE_LENGTH or movie_title_length > MAX_MOVIE_TITLE_LENGTH:
                raise UnprocessableEntity(
                    description=f'Movie title length must be between {MIN_MOVIE_TITLE_LENGTH} and {MAX_MOVIE_TITLE_LENGTH}'
                )

        if check_release_date:
            try:
                movie_data['release_date'] = datetime.fromtimestamp(release_date)
            except Exception:
                raise UnprocessableEntity(
                    description=f'Could not create date and time from value {release_date}'
                )

        return movie_data

    @app.route('/actors', methods=['POST'])
    @requires_auth(permission='create:actors')
    def create_actor():
        try:
            actor_data = {
                'name': request.get_json()['name'],
                'gender': request.get_json()['gender'],
                'age': request.get_json()['age']
            }

            actor_data = validate_actor(**actor_data, updating=True)

            actor = Actors(**actor_data)
            actor.insert()
            response = {
                'success': True,
                'actors': [actor.format()]
            }
        except UnprocessableEntity:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth(permission='update:actors')
    def update_actor(actor_id):
        try:
            actor = Actors.query.get(actor_id)
            if not actor:
                raise

            actor_props = ['name', 'gender', 'age']
            actor_data = {}

            for prop in actor_props:
                if prop in request.get_json():
                    actor_data[prop] = request.get_json()[prop]

            actor_data = validate_actor(**actor_data)

            for prop, val in actor_data.items():
                setattr(actor, prop, val)

            update()
            response = {
                'success': True,
                'actors': [actor.format()]
            }
        except UnprocessableEntity:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth(permission='delete:actors')
    def delete_actor(actor_id):
        try:
            actor = Actors.query.get(actor_id)
            if not actor:
                raise NotFound

            actor.delete()
            response = {
                'success': True,
                'delete': actor_id
            }
        except NotFound:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/movies', methods=['POST'])
    @requires_auth(permission='create:movies')
    def create_movie():
        try:
            movie_data = {
                'title': request.get_json()['title'],
                'release_date': request.get_json()['release_date']
            }

            movie_data = validate_movie(**movie_data, updating=True)

            movie = Movies(**movie_data)
            movie.insert()
            response = {
                'success': True,
                'movies': [movie.format()]
            }
        except UnprocessableEntity:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    # Error Handling
    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        code = e.code if hasattr(e, 'code') else 500
        description = e.description if hasattr(e, 'description') else 'Please contact the server admin'
        response_body = {
            "code": code,
            "description": description,
        }

        if hasattr(e, 'message'):
            response_body['message'] = e.message

        return jsonify(response_body), code

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080)
