import datetime
import random
import string
import jwt
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from flask import current_app, abort, jsonify, request
from cliqcard_server.models import db, OAuthToken

from authlib.flask.oauth2.sqla import create_bearer_token_validator
from authlib.flask.oauth2 import ResourceProtector, current_token


def format_phone_number(phone_number):
    # check if phone number has leading '+', if not add it for the phonenumbers parser
    if phone_number and phone_number[0] != '+':
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


def generate_short_code(n, letters=True):
    if letters:
        characters = string.ascii_uppercase + string.digits
    else:
        characters = string.digits
    return ''.join(random.choice(characters) for _ in range(n))


BearerTokenValidator = create_bearer_token_validator(db.session, OAuthToken)
ResourceProtector.register_token_validator(BearerTokenValidator())

require_oauth = ResourceProtector()