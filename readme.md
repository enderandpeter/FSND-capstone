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
   The client secret and ID for a Machine-to-Machine test application are recommended.
   * Credentials for the test users (Casting Assistant, Casting Director, and Executive Producer):
     * `TEST_CA_USER`, `TEST_CA_PASS`
     * `TEST_CD_USER`, `TEST_CD_PASS`
     * `TEST_EP_USER`, `TEST_EP_PASS`
2. Run `python test_app.py`

## Users

User authentication, and authorization are managed by Auth0.

Currently, if you registered a new account, you'd still not access anything without a role with permissions.
These are manually attributed for the time being, so the Postman collection will contain JWTs that can be used
in the frontend. Also, there are test credentials available for each role, which are used in the tests to obtain
access tokens from the Machine-to-Machine test application.

### Permissions

These permissions are in the `permissions` property of the JWT payload, as you might expect. 

#### Casting Assistants

* *get:actors* 
