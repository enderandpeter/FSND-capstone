import os
import sys
from flask import Flask, request, abort, jsonify
from werkzeug.exceptions import BadRequest, HTTPException, UnprocessableEntity
from flask_cors import CORS
from auth import requires_auth

from models import setup_db, Actors, Movies, MAX_ACTOR_NAME_LENGTH, MIN_ACTOR_NAME_LENGTH, MIN_ACTOR_AGE, MAX_ACTOR_AGE


def create_app(test_config=None):
    app = Flask(__name__)
    if type(test_config) == dict:
        setup_db(app, **test_config)
    else:
        setup_db(app)

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

    def validate_actor(name=None, gender=None, age=None, updating=None):
        check_name = True if not updating and name is not None else False
        check_gender = True if not updating and gender is not None else False
        check_age = True if not updating and age is not None else False

        actor_data = {}

        if check_name:
            actor_data = {
                'name': name.strip()
            }

            actor_name_length = len(actor_data['name'])
            if actor_name_length == 0 or actor_name_length > MAX_ACTOR_NAME_LENGTH:
                raise UnprocessableEntity(
                    description=f'Actor name length must be between {MIN_ACTOR_NAME_LENGTH} and {MAX_ACTOR_NAME_LENGTH}'
                )

        if check_gender:
            actor_data['gender'] = gender.lower().strip()

            if actor_data['gender'] is not 'm' or actor_data['gender'] is not 'f':
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

    @app.route('/actors', methods=['POST'])
    @requires_auth(permission='create:actors')
    def create_actor():
        try:
            actor_data = {
                'name': request.get_json()['name'],
                'gender': request.get_json()['gender'],
                'age': request.get_json()['age']
            }

            actor_data = validate_actor(**actor_data)

            actor = Actors(**actor_data)
            actor.insert()
            response = {
                'success': True,
                'actor': [actor.format()]
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
