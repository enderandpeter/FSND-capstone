from werkzeug.exceptions import BadRequest, Unauthorized, NotFound


class TokenExpired(BadRequest):
    message = 'token_expired'
    description = 'Token has expired'


class PermissionsNotFound(BadRequest):
    message = 'no_permissions'
    description = 'Permissions not included in JWT.'


class AuthHeaderMissing(Unauthorized):
    message = 'authorization_header_missing'
    description = 'Authorization header is expected.'


class AuthHeaderInvalid(BadRequest):
    message = 'invalid_header'
    description = 'Authorization header must start with "Bearer".'


class DrinkNotFound(NotFound):
    message = 'not_found'
    description = 'Drink not found'
