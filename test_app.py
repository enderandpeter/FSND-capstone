import os
import json
import unittest
from app import create_app
from urllib.request import urlopen
from urllib.parse import urlencode


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

    def ca_get(self, data_type):
        """
        Get data as a Casting Assistant
        :return:
        """

        token = CastingTestCase.get_access_token('CA')

        return self.client().get(f'/{data_type}', headers={
            'Authorization': f'Bearer {token}'
        })

    def ca_post(self, data_type):
        """
        Try to create the entity as a Casting Assistant
        :return:
        """

        token = CastingTestCase.get_access_token('CA')

        return self.client()\
            .post(f'/{data_type}',
                 headers={
                    'Authorization': f'Bearer {token}'
                },
                 json={
                     "name": "Clarece",
                     "gender": "f",
                     "age": 88
            })

    def cd_get(self, data_type):
        """
        Get data as a Casting Assistant
        :return:
        """

        token = CastingTestCase.get_access_token('CD')

        return self.client().get(f'/{data_type}', headers={
            'Authorization': f'Bearer {token}'
        })

    def cd_post(self, data_type):
        """
        Try to create the entity as a Casting Assistant
        :return:
        """

        token = CastingTestCase.get_access_token('CD')

        return self.client() \
            .post(f'/{data_type}',
                  headers={
                      'Authorization': f'Bearer {token}'
                  },
                  json={
                      "name": "Clarece",
                      "gender": "f",
                      "age": 88
                  })

    def public_get(self, data_type):
        """
        Get data as a member of the public
        :return:
        """

        return self.client().get(f'/{data_type}')

    def test_ca_get(self):
        """"
        Casting Assistants can get their permitted data
        """
        data = ['actors', 'movies']

        for data_type in data:
            actors_response = self.ca_get(data_type)
            self.assertEqual(actors_response.json, {f'{data_type}': []})

    def test_ca_post(self):
        """"
        Casting Assistants cannot create actors
        """
        data = ['actors']
        for data_type in data:
            actors_response = self.ca_post(data_type)
            self.assertEqual(actors_response.json['code'], 401)

    def test_cd_post(self):
        """"
        Casting Assistants can create actors
        """
        data = ['actors']
        for data_type in data:
            actors_response = self.cd_post(data_type)
            self.assertEqual(actors_response.json, {f'{data_type}': [
                {'name': 'Clarece', 'gender': 'Female', 'id': 1, 'age': 88, 'movies': []}
            ], 'success': True})

    def test_public_get(self):
        """"
        The public cannot get authenticated data
        """
        data = ['actors', 'movies']
        for data_type in data:
            actors_response = self.public_get(data_type)
            self.assertEqual(actors_response.json['code'], 401)


if __name__ == '__main__':
    unittest.main()
