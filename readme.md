# The Kid Stays in the Picture!

A web app for studios and agencies to manage actors cast in movies.
This is the final project for [Udacity's Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044)

## Prerequisites

Tested on:

* Python 3.7
* Postgres 12.1

## Installation

1. Run `pip install -r requirements.txt`
2. Set the environment variables:
   * `DATABASE_URL` - The database URL for the app (e.g. `postgres://postgres:postgres@localhost/casting`)
   * `AUTH0_DOMAIN=mydomain.auth0.com`, `ALGORITHMS=RS256`, `API_AUDIENCE=casting` - Auth0 settings. Separate algorithms with commas.
3. Run `flask db upgrade` to create all the tables
   
## Deployment

### Dev

1. Set the environment variable:
   * `FLASK_ENV=development`
2. Run `python app.py`

### Prod

1. Run `gunicorn app:APP`

See the bottom of `app.py` for the run settings. The server will run on port 8080 and any IP from which it can be reached.

## Testing

1. Set the environment variable:
   * `DATABASE_TEST_URL` - The test database URL
   * `AUTH0_CLIENT_SECRET`, `AUTH0_CLIENT_ID` - Set these to the Auth0 client secret and ID for the Auth0 application used to get access tokens for test users.
   The credentials for a Machine-to-Machine test application are recommended.
   * `TEST_CA_USER`, `TEST_CA_PASS` - Credentials for the test Casting Assistant user
2. Run `python test_app.py`
