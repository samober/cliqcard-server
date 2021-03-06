import time
from flask import request, jsonify, Blueprint
from authlib.flask.oauth2 import current_token
from authlib.common.security import generate_token
from cliqcard_server.models import db, User, RegistrationToken, OAuthClient, OAuthToken, ProfilePicture, Phone
from cliqcard_server.serializers import serialize_account
from cliqcard_server.utils import require_oauth, format_phone_number
from cliqcard_server.extensions import bcrypt
from cliqcard_server.errors import InvalidRequestError, UnauthorizedError
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/', methods=['GET', 'PUT', 'DELETE'])
@require_oauth(None)
def index():
    if request.method == 'GET':
        return jsonify(serialize_account(current_token.user))
    elif request.method == 'PUT':
        # get the current user
        user = current_token.user
        # update specified fields
        user.first_name = request.json.get('first_name', user.first_name)
        user.last_name = request.json.get('last_name', user.last_name)
        # save
        db.session.commit()
        # return the account
        return jsonify(serialize_account(user))
    elif request.method == 'DELETE':
        db.session.delete(current_token.user)
        db.session.commit()
        return ('', 204)


@account.route('/', methods=['POST'])
def post():
    # get client credentials
    client_id = request.json.get('client_id')
    client_secret = request.json.get('client_secret')

    # find the client
    client = OAuthClient.query.filter_by(client_id=client_id, client_secret=client_secret).first()
    if not client:
        raise UnauthorizedError(message='Invalid client credentials')

    # get phone number and registration token
    phone_number = request.json.get('phone_number')
    raw_registration_token = request.json.get('registration_token')

    # get other required user details
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')

    if phone_number is None:
        raise InvalidRequestError('Missing \'phone_number\' parameter')
    if raw_registration_token is None:
        raise InvalidRequestError('Missing \'registration_token\' parameter')
    if first_name is None:
        raise InvalidRequestError('Missing \'first_name\' parameter')
    if last_name is None:
        raise InvalidRequestError('Missing \'last_name\' parameter')

    # validate/format phone number
    phone_number = format_phone_number(phone_number)
    if not phone_number:
        raise InvalidRequestError('Invalid phone number. You must send phone numbers in e164 format')

    # find the matching registration token for this phone number
    registration_token = RegistrationToken.query.filter_by(phone_number=phone_number).first()
    if not registration_token:
        raise UnauthorizedError()
    elif registration_token.is_expired():
        # token is expired - delete from database
        db.session.delete(registration_token)
        db.session.commit()
        raise InvalidRequestError('The registration code for that phone number has expired')

    # check if the tokens match
    if not bcrypt.check_password_hash(registration_token.token, raw_registration_token):
        # no match - wrong token
        raise UnauthorizedError()

    # delete the registration token
    db.session.delete(registration_token)

    # create a new user
    user = User(
        first_name=first_name,
        last_name=last_name
    )
    db.session.add(user)

    # create a new primary phone
    user.phones = [Phone(type='mobile', number=phone_number, is_primary=True)]

    # commit the session - important because we need the user id
    db.session.commit()

    # generate an access token for the user
    token = OAuthToken()
    token.client_id = client.client_id,
    token.token_type = 'Bearer',
    token.access_token = generate_token(),
    token.refresh_token = generate_token(),
    token.issued_at = int(time.time()),
    token.expires_in = 3600,
    token.user_id = user.id
    db.session.add(token)

    # commit the session
    db.session.commit()

    # respond with the newly created account info
    response = jsonify({
        'token': {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token,
            'token_type': token.token_type,
            'expires_in': token.expires_in
        },
        'user': serialize_account(user)
    })
    response.status_code = 201
    return response


@account.route('/picture', methods=['POST', 'DELETE'])
@require_oauth(None)
def update_picture():
    if request.method == 'POST':
        file_to_upload = request.files['file']
        if not file_to_upload:
            raise InvalidRequestError(message="You must specify the 'file' parameter")
        upload_result = upload(file_to_upload)

        # create a new profile picture object
        profile_picture = ProfilePicture()
        profile_picture.original = upload_result['secure_url']
        profile_picture.thumb_big, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=128, height=128)
        profile_picture.thumb_normal, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=84, height=84)
        profile_picture.thumb_small, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=58, height=58)
        profile_picture.thumb_mini, _ = cloudinary_url(upload_result['public_id'], format='jpg', crop='fill', width=32, height=32)

        # add to the user
        current_token.user.profile_picture = profile_picture

        # commit
        db.session.commit()

        return jsonify(serialize_account(current_token.user))
    elif request.method == 'DELETE':
        # remove the current user's profile picture
        current_token.user.profile_picture = None
        # save
        db.session.commit()
        return jsonify(serialize_account(current_token.user))
