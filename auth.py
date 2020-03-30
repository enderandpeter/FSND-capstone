import json
import os
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from werkzeug.exceptions import Unauthorized

from errors import AuthHeaderMissing, AuthHeaderInvalid, PermissionsNotFound, TokenExpired

auth0_settings_names = ['AUTH0_DOMAIN', 'ALGORITHMS', 'API_AUDIENCE']
auth0_settings = {setting: os.environ[setting] for setting in auth0_settings_names}
auth0_settings['ALGORITHMS'] = auth0_settings['ALGORITHMS'].split(',')

# Much of the following is from BasicFlaskAuth

# Auth Header
def get_token_auth_header():
    """
    Obtains the access token from the authorization header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthHeaderMissing

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthHeaderInvalid

    elif len(parts) == 1:
        raise AuthHeaderInvalid(description='Token not found')

    elif len(parts) > 2:
        raise AuthHeaderInvalid(description='Authorization header must be bearer token.')

    token = parts[1]
    return token


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise PermissionsNotFound

    if permission not in payload['permissions']:
        raise Unauthorized(description='Permission not found.')
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{auth0_settings["AUTH0_DOMAIN"]}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthHeaderInvalid(description='Authorization malformed.')

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=auth0_settings['ALGORITHMS'],
                audience=auth0_settings['API_AUDIENCE'],
                issuer=f'https://{auth0_settings["AUTH0_DOMAIN"]}/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpired

        except jwt.JWTClaimsError:
            raise AuthHeaderInvalid(description='Incorrect claims. Please, check the audience and issuer.')
        except Exception:
            raise AuthHeaderInvalid(description='Unable to parse authentication token.')
    raise AuthHeaderInvalid(description='Unable to find the appropriate key.')


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(*args, **kwargs)

        return wrapper

    return requires_auth_decorator
