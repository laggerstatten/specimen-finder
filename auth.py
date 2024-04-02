import json
import os
import sys
from flask import request, _request_ctx_stack, abort, session
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from os import environ

# TODO move to file

'''#AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_DOMAIN = 'dev-2bm0ojvr4sfeljpt.us.auth0.com'

#ALGORITHMS = os.getenv('ALGORITHMS')
ALGORITHMS = ['RS256']

#API_AUDIENCE = os.getenv('API_AUDIENCE')
API_AUDIENCE = 'id_specimen_finder'''

# Get environment variables
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = os.getenv('ALGORITHMS')
API_AUDIENCE = os.getenv('API_AUDIENCE')

# Check if environment variables are set
if not AUTH0_DOMAIN or not ALGORITHMS or not API_AUDIENCE:
    raise Exception("Missing required environment variables")





# AuthError Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    if 'Authorization' not in request.headers:
        abort(401)
    
    else:
        auth_headers = request.headers['Authorization']
        if auth_headers:
            bearer_token_array = auth_headers.split(' ')
            if bearer_token_array[0] and bearer_token_array[0].lower() == 'bearer' and bearer_token_array[1]:
                return bearer_token_array[1]
            else:
                abort(401)


# Check Permission
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(400)
    if permission not in payload['permissions']:
        abort(403)
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        abort(401)

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
                algorithms = ALGORITHMS,
                audience = API_AUDIENCE,
                issuer = f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            abort(401)

        except jwt.JWTClaimsError:
            abort(401)
        except Exception:
            abort(400)
    abort(400)



def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Check if running in a web application
            if request and request.headers.get('Content-Type') != 'application/json':
                # Check if token exists in the session
                if 'token' in session:
                    token = session['token']
                    print("session token")
                    print(token)                    
                else:
                    # If token is not in the session, abort with 400
                    abort(400)
            else:
                # If not running in a web application or token not in session, check for token in headers
                token = get_token_auth_header()
                print('token at authorization time: {}'.format(token))
                if token is None:
                    abort(400)
            try:
                # Verify and decode JWT token
                payload = verify_decode_jwt(token)
                print('Payload: {}'.format(payload))
                print(f'checking for permission: {permission}')
                if check_permissions(permission, payload):
                    print('Permission found')
            except:
                # If token verification fails, abort with 401
                abort(401)
            # Check permissions
            check_permissions(permission, payload)
            # Call the decorated function with payload and other arguments
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


