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
   * `DATABASE_URL` - The database URL for the app
   * `AUTH0_DOMAIN`, `ALGORITHMS`, `API_AUDIENCE` - Auth0 settings
3. Run `flask db upgrade` to create all the tables
   
## Deployment

### Dev

1. Set the environment variable:
   * `FLASK_DEBUG=1`
2. Run `python app.py`

### Prod

1. Run `gunicorn app:APP`

See the bottom of `app.py` for the run settings. The server will run on port 8080 and any IP from which it can be reached.

## Testing

1. Set the environment variable:
   * `DATABASE_TEST_URL` - The test database URL
2. Run `python test_app.py`
