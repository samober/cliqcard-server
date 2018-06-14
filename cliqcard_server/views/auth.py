import secrets
from flask import request, jsonify, Blueprint
from cliqcard_server.models import db, User, PhoneToken, RegistrationToken
from cliqcard_server.extensions import bcrypt, twilio_client, twilio_phone_number
from cliqcard_server.utils import format_phone_number, generate_short_code
from cliqcard_server.errors import InvalidRequestError, UnauthorizedError


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/phone', methods=['POST'])
def phone():
    phone_number = request.json.get('phone_number')
    # validate/format phone number
    phone_number = format_phone_number(phone_number)
    if not phone_number:
        raise InvalidRequestError('Invalid phone number. You must send phone numbers in valid international format')

    # create a random validation code
    code = generate_short_code(6, letters=False)

    # find and remove any existing phone tokens for this phone number
    for phone_token in PhoneToken.query.filter_by(phone_number=phone_number):
        db.session.delete(phone_token)

    # save a new phone token
    phone_token = PhoneToken(
        phone_number=phone_number,
        code=code
    )
    db.session.add(phone_token)
    db.session.commit()

    # send the code to the phone number over SMS
    twilio_client.messages.create(
        to=phone_number,
        from_=twilio_phone_number,
        body='Your CliqCard validation code is: %s' % code
    )
    # print('Code: %s' % code)

    # try to find a user with this phone number
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        # no user associated with this phone
        return jsonify({
            'phone_number_registered': False,
            'phone_number': phone_number
        })
    else:
        # send back the user's first name so client device's can welcome them
        return jsonify({
            'phone_number_registered': True,
            'phone_number': phone_number,
            'user': {
                'first_name': user.first_name
            }
        })


@oauth.route('/register', methods=['POST'])
def register():
    phone_number = request.json.get('phone_number')
    code = request.json.get('code')

    # validate/format phone number
    phone_number = format_phone_number(phone_number)
    if not phone_number:
        raise InvalidRequestError('Invalid phone number. You must send phone numbers in valid international format')

    # try to find a matching phone token
    phone_token = PhoneToken.query.filter_by(phone_number=phone_number, code=code).first()

    if not phone_token:
        raise UnauthorizedError()
    elif phone_token.is_expired():
        # token is expired - delete from database
        db.session.delete(phone_token)
        db.session.commit()
        raise InvalidRequestError('The validation code for that number has expired')
    else:
        # check to make sure there is not already an account with this number
        user = User.query.filter_by(phone_number=phone_number).first()
        if user is not None:
            # user already exists
            raise UnauthorizedError()

        # phone number validated, delete the phone token
        db.session.delete(phone_token)

        # delete any existing registration tokens for this phone number
        for registration_token in RegistrationToken.query.filter_by(phone_number=phone_number):
            db.session.delete(registration_token)

        # create a new registration token - use bcrypt to hash the raw token
        raw_token = secrets.token_urlsafe(64)
        registration_token = RegistrationToken(
            phone_number=phone_number,
            token=bcrypt.generate_password_hash(raw_token).decode('utf-8')
        )
        db.session.add(registration_token)
        # commit the session
        db.session.commit()

        # respond with the registration token
        return jsonify({
            'phone_number': phone_number,
            'registration_token': raw_token,
            'expires_in': registration_token.expires_in
        })