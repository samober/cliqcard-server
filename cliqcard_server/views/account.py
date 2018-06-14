from flask import request, jsonify
from flask.views import MethodView
from authlib.flask.oauth2 import current_token
from cliqcard_server.models import db, User, RegistrationToken, Card
from cliqcard_server.serializers import serialize_account
from cliqcard_server.utils import require_oauth, format_phone_number
from cliqcard_server.extensions import bcrypt
from cliqcard_server.errors import InvalidRequestError, UnauthorizedError


class AccountView(MethodView):
    """
    Handles the /account endpoint for getting, updating, and deleting accounts.
    """

    @require_oauth(None)
    def get(self):
        return jsonify(serialize_account(current_token.user))


    def post(self):
        # get phone number and registration token
        phone_number = request.json.get('phone_number')
        raw_registration_token = request.json.get('registration_token')

        # get other required user details
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')

        if first_name is None:
            raise InvalidRequestError('Missing \'first_name\' parameter')
        if last_name is None:
            raise InvalidRequestError('Missing \'last_name\' parameter')

        # get optional user details
        email = request.json.get('email', None)

        # validate/format phone number
        phone_number = format_phone_number(phone_number)
        if not phone_number:
            raise InvalidRequestError('Invalid phone number. You must send phone numbers in valid international format')

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
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(user)

        # commit the session - important because we need the user id
        db.session.commit()

        # create personal and work cards for the user
        user.personal_card = Card(phone1=phone_number, email=email)
        user.work_card = Card()

        # commit the session
        db.session.commit()

        # respond with the newly created account info
        response = jsonify(serialize_account(user))
        response.status_code = 201
        return response

    @require_oauth(None)
    def put(self):
        user = current_token.user

        phone_number = request.json.get('phone_number')
        if phone_number is not None:
            # validate/format phone number
            phone_number = format_phone_number(phone_number)
            if not phone_number:
                raise InvalidRequestError('Invalid phone number. You must send phone numbers in valid international format')

        user.phone_number = phone_number if phone_number is not None else user.phone_number
        user.first_name = request.json.get('first_name', user.first_name)
        user.last_name = request.json.get('last_name', user.last_name)
        user.email = request.json.get('email', user.email)

        db.session.commit()

        return jsonify(serialize_account(user))

    @require_oauth(None)
    def delete(self):
        db.session.delete(current_token.user)
        db.session.commit()
        return ('', 204)