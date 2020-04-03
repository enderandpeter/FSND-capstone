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

All environment variable values will be provided separately so that no sensitve data is committed. 

### Dev

1. Set the environment variable:
   * `FLASK_ENV=development`
   * `FLASK_DEBUG=1`
2. Run `python app.py`

### Prod

1. Run `gunicorn app:APP`

See the bottom of `app.py` for the run settings. The server will run on port 8080 and any IP from which it can be reached.

### Testing

1. Set the environment variable:
   * `DATABASE_TEST_URL` - The test database URL
   * `AUTH0_CLIENT_SECRET`, `AUTH0_CLIENT_ID` - Set these to the Auth0 client secret and ID for the Auth0 application used to get access tokens for test users.
   The client secret and ID for a Machine-to-Machine test application are recommended.
   * Credentials for the test users (Casting Assistant, Casting Director, and Executive Producer):
     * `TEST_CA_USER`, `TEST_CA_PASS`
     * `TEST_CD_USER`, `TEST_CD_PASS`
     * `TEST_EP_USER`, `TEST_EP_PASS`
   * Other required test env variables:
     * `TEST_EXPIRED_TOKEN` - An expired JWT
2. Run `python test_app.py`

## Authentication and Authorization

User authentication and authorization are managed by Auth0. Login credentials will be provided for review. You can obtain
JWTs in the following ways:

* For project submission, a Postman collection will be included with collections variables *ep_token*, *cd_token*, and *ca_token*
that are set to the JWT for an Executive Producer, Casting Director, and Casting Assistant.
* Make a request to `https://${AUTH0_DOMAIN}/authorize?audience=${API_AUDIENCE}&response_type=code&client_id=${AUTH0_CLIENT_ID}`, login with
the credentials you will be provided and you will be redirected to a dead URL from which you can obtain the JWT from the `access_token` parameter.
* Make a [Resource Owner Pasword Grant request](https://auth0.com/docs/api-auth/tutorials/password-grant#ask-for-a-token) which will
return a JWT in the `access_token` property of the response data:

```
curl --request POST \
  --url 'https://${AUTH0_DOMAIN}/oauth/token' \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data grant_type=password \
  --data username=${TEST_CA_USER} \
  --data 'password=${TEST_CA_PASS}' \
  --data audience=${API_AUDIENCE} \
  --data 'client_id=${AUTH0_CLIENT_ID}' \
  --data client_secret=${AUTH0_CLIENT_SECRET}
```

# API Documentation

Please see the [Casting API documentation](https://documenter.getpostman.com/view/3237152/SzYaTwwX) for important details on the REST API.
The intro describes how the doc is structured. Example request and responses are on the right-hand side.
