import os
import sys
from flask import Flask, request, abort, jsonify
from werkzeug.exceptions import BadRequest, HTTPException
from flask_cors import CORS
from auth import requires_auth

from models import setup_db, Actors, Movies


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
