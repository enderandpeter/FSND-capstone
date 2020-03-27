import os
import unittest
from flask_migrate import upgrade, downgrade
from app import create_app


class CastingTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        if 'DATABASE_TEST_URL' not in os.environ:
            raise KeyError('Please set the DATABASE_TEST_URL env variable to the URL of an existing database')

        config = {'test_config': os.environ['DATABASE_TEST_URL']}
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


if __name__ == '__main__':
    unittest.main()
