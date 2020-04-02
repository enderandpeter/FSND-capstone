import os
import json
import unittest
from app import create_app
from urllib.request import urlopen
from urllib.parse import urlencode
from datetime import datetime
from werkzeug.wrappers import Response

from models import Actors, Movies


class CastingTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        if 'DATABASE_TEST_URL' not in os.environ:
            raise KeyError('Please set the DATABASE_TEST_URL env variable to the URL of an existing database')

        config = {
            'test_config': {
                'database_path': os.environ['DATABASE_TEST_URL']
            }
        }
        self.app = create_app(**config)
        self.client = self.app.test_client

        # binds the app to the current context
        with self.app.app_context():
            self.app.db.create_all()

    def tearDown(self):
        with self.app.app_context():
            self.app.db.drop_all()

    @staticmethod
    def get_access_token(user=None):
        """
        Get a user access token
        :param user: Either 'CD' or 'CA'
        :return:
        """
        user_type = user.upper()
        data = {
            'grant_type': 'password',
            'username': os.environ[f"TEST_{user_type}_USER"],
            'password': os.environ[f"TEST_{user_type}_PASS"],
            'audience': 'casting',
            'client_id': os.environ["AUTH0_CLIENT_ID"],
            'client_secret': os.environ["AUTH0_CLIENT_SECRET"]
        }
        token_url = urlopen(f'https://{os.environ["AUTH0_DOMAIN"]}/oauth/token', data=str.encode(urlencode(data)))
        token_response = json.loads(token_url.read())

        return token_response['access_token']

    def user_get(self, user_type, entity_type):
        """
        Get data as a certain type of user
        :return:
        """

        token = CastingTestCase.get_access_token(user_type)

        return self.client().get(f'/{entity_type}', headers={
            'Authorization': f'Bearer {token}'
        })

    def user_post(self, user_type, entity_type, request_data) -> Response:
        """
        Post data as a user
        :return:
        """

        token = CastingTestCase.get_access_token(user_type)

        return self.client() \
            .post(f'/{entity_type}',
                  headers={
                      'Authorization': f'Bearer {token}'
                  },
                  json=request_data)

    def user_patch(self, user_type, entity_type, entity_id, request_data):
        """
        Update data as a user
        :return:
        """

        token = CastingTestCase.get_access_token(user_type)

        return self.client() \
            .patch(f'/{entity_type}/{entity_id}',
                  headers={
                      'Authorization': f'Bearer {token}'
                  },
                  json=request_data)

    def user_delete(self, user_type, entity_type, entity_id):
        """
        Delete an entity as a user
        :return:
        """

        token = CastingTestCase.get_access_token(user_type)

        return self.client() \
            .delete(f'/{entity_type}/{entity_id}',
                  headers={
                      'Authorization': f'Bearer {token}'
                  }
            )

    def public_get(self, data_type):
        """
        Get data as a member of the public
        :return:
        """

        return self.client().get(f'/{data_type}')

    def test_ca(self):
        self.get('CA')
        self.post('CA')
        self.patch('CA')
        self.delete('CA')

    def test_cd(self):
        self.get('CD')
        self.post('CD')
        self.patch('CD')
        self.delete('CD')

    def test_ep(self):
        self.get('EP')
        self.post('EP')
        self.patch('EP')
        self.delete('EP')

    def get(self, user_type):
        """"
        Get permitted data
        """
        data = ['actors', 'movies']

        for data_type in data:
            actors_response = self.user_get(user_type, data_type)
            self.assertEqual(actors_response.json, {f'{data_type}': []})

    def post(self, user_type):
        """"
        Create actors or movies
        """
        data = ['actors', 'movies']
        for entity_type in data:

            if entity_type is 'actors':
                actors_response = self.user_post(user_type, entity_type, {
                     "name": "Clarece",
                     "gender": "f",
                     "age": 88
                })
                if user_type is 'CA':
                    self.assertEqual(actors_response.json['code'], 401)
                else:
                    self.assertEqual(actors_response.json, {f'{entity_type}': [
                        {'name': 'Clarece', 'gender': 'Female', 'id': 1, 'age': 88, 'movies': []}
                    ], 'success': True})

            if entity_type is 'movies':
                movies_response = self.user_post(user_type, entity_type, {
                    "title": "The Big One",
                    "release_date": datetime.fromisoformat('2020-03-22 22:23:11').timestamp()
                })
                if user_type is 'EP':
                    self.assertEqual(movies_response.json, {
                        'success': True,
                        'movies': [{
                            'id': 1,
                            'title': "The Big One",
                            'release_date': 'Sun Mar 22 22:23:11 2020',
                            'actors': []
                        }]
                    })
                else:
                    self.assertEqual(movies_response.json['code'], 401)

    def patch(self, user_type):
        """"
        Casting Assistants cannot edit actors nor movies
        """
        data = ['actors', 'movies']
        for entity_type in data:

            if entity_type == 'actors':
                actor_data = {
                    "name": "Clarece",
                    "gender": "f",
                    "age": 88
                }
                actor = Actors(**actor_data)
                actor.insert()

                actors_response = self.user_patch(user_type, entity_type, 1, {
                    "name": "Amanda"
                })

                if user_type is 'CA':
                    self.assertEqual(actors_response.json['code'], 401)
                else:
                    self.assertEqual(actors_response.json, {f'{entity_type}': [
                        {'name': 'Amanda', 'gender': 'Female', 'id': 1, 'age': 88, 'movies': []}
                    ], 'success': True})

            if entity_type == 'movies':
                movie_data = {
                    "title": "The Big One",
                    "release_date": datetime.fromisoformat('2020-03-22 22:23:11')
                }
                movie = Movies(**movie_data)
                movie.insert()

                movies_response = self.user_patch(user_type, entity_type, 1, {
                    "title": "The Little One"
                })

                if user_type is 'CA':
                    self.assertEqual(movies_response.json['code'], 401)
                else:
                    self.assertEqual(movies_response.json, {
                        'success': True,
                        'movies': [{
                            'id': 1,
                            'title': "The Little One",
                            'release_date': 'Sun Mar 22 22:23:11 2020',
                            'actors': []
                        }]
                    })

    def delete(self, user_type):
        """"
        Delete actors or movies
        """
        data = ['actors', 'movies']
        for entity_type in data:
            if entity_type == 'actors':
                actor_data = {
                    "name": "Clarece",
                    "gender": "f",
                    "age": 88
                }
                actor = Actors(**actor_data)
                actor.insert()

                actors_response = self.user_delete(user_type, entity_type, 1)
                if user_type is 'CA':
                    self.assertEqual(actors_response.json['code'], 401)
                    with self.app.app_context():
                        self.assertIsNotNone(self.app.db.session.query(Movies).get(1))
                else:
                    self.assertEqual(actors_response.json, {'delete': 1, 'success': True})
                    with self.app.app_context():
                        self.assertIsNone(self.app.db.session.query(Actors).get(1))

            if entity_type == 'movies':
                movie_data = {
                    "title": "The Big One",
                    "release_date": datetime.fromisoformat('2020-03-22 22:23:11')
                };
                movie = Movies(**movie_data)
                movie.insert()

                movies_response = self.user_delete(user_type, entity_type, 1)
                if user_type is 'EP':
                    self.assertEqual(actors_response.json, {'delete': 1, 'success': True})
                    with self.app.app_context():
                        self.assertIsNone(self.app.db.session.query(Movies).get(1))
                else:
                    self.assertEqual(movies_response.json['code'], 401)
                    with self.app.app_context():
                        self.assertIsNotNone(self.app.db.session.query(Movies).get(1))

    def test_relationship(self):
        movies1 = self.user_post('EP', 'movies', {
            "title": 'The Way',
            "release_date": datetime.today().timestamp()
        })
        movies2 = self.user_post('EP', 'movies', {
            "title": 'The Road',
            "release_date": datetime.today().timestamp()
        })
        movies3 = self.user_post('EP', 'movies', {
            "title": 'The Ringer',
            "release_date": datetime.today().timestamp()
        })

        actor1 = self.user_post('CD', 'actors', {
            "name": 'Carol',
            "gender": 'f',
            "age": 30,
            "movies": [1,2]
        })
        actor2 = self.user_post('CD', 'actors', {
            "name": 'John',
            "gender": 'm',
            "age": 20,
            "movies": [3]
        })
        actor3 = self.user_post('CD', 'actors', {
            "name": 'Jan',
            "gender": 'f',
            "age": 10,
            "movies": [1]
        })

        self.assertEqual(actor1.json['actors'][0]['movies'][1]['title'], 'The Road')
        self.assertEqual(len(actor2.json['actors'][0]['movies']), 1)

        movie1 = self.user_get('CA', 'movies')
        self.assertEqual(len(movie1.json['movies'][0]['actors']), 2)

    def test_public_get(self):
        """"
        The public cannot get authenticated data
        """
        data = ['actors', 'movies']
        for entity_type in data:
            actors_response = self.public_get(entity_type)
            self.assertEqual(actors_response.json['code'], 401)


if __name__ == '__main__':
    unittest.main()
