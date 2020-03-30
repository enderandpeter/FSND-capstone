import os
import json
import unittest
from flask_migrate import upgrade, downgrade
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
            upgrade()

    def tearDown(self):
        with self.app.app_context():
            downgrade()

    def test_index(self):
        response = self.client().get('/')
        self.assertEqual(b'Hello', response.data)

    def test_get_actors(self):
        """
        Each user role should have access controlled by their permissions
        :return:
        """

        data = {
            'grant_type': 'password',
            'username': os.environ["TEST_CA_USER"],
            'password': os.environ["TEST_CA_PASS"],
            'audience': 'casting',
            'client_id': os.environ["AUTH0_CLIENT_ID"],
            'client_secret': os.environ["AUTH0_CLIENT_SECRET"]
        }
        token_url = urlopen(f'https://{os.environ["AUTH0_DOMAIN"]}/oauth/token', data=str.encode(urlencode(data)))
        token_response = json.loads(token_url.read())

        token = token_response['access_token']

        actors_response = self.client().get('/actors', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertDictEqual(actors_response.json, {'actors': []})


if __name__ == '__main__':
    unittest.main()
