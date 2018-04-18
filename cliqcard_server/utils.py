import datetime
from functools import wraps
import jwt
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from flask import current_app, abort, jsonify, request
from cliqcard_server.models import User


def format_phone_number(phone_number):
    # check if phone number has leading '+', if not add it for the phonenumbers parser
    if phone_number[0] != '+':
        phone_number = '+%s' % phone_number
    try:
        # parse the phone number
        parsed = phonenumbers.parse(phone_number, None)
        # format number in international format
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        # if the phone number is invalid return None
        return None

def generate_access_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # get the access token from the Authorization header
        auth_header = request.headers['Authorization']
        if auth_header and len(auth_header.split(' ')) == 2:
            # Accept auth header formats:
            #   'Token <access_token>'
            access_token = auth_header.split(' ')[1]
        else:
            access_token = None
        if not access_token:
            abort(401)
        # decode the payload
        try:
            payload = jwt.decode(access_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            response = jsonify({
                'error': 'This access token has expired',
                'error_code': 'expired_access_token'
            })
            response.status_code = 401
            return response
        if not payload:
            abort(401)
        # find the user with the given id
        request.user = User.query.get(payload['user_id'])
        if not request.user:
            abort(401)
        return f(*args, **kwargs)
    return decorated