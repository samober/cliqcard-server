import random
import string
import datetime
import time
import secrets
from flask import request, jsonify, abort
from flask.views import View
from cliqcard_server.models import db, User, PhoneToken, RegistrationToken, RefreshToken
from cliqcard_server.serializers import serialize_account
from cliqcard_server.extensions import bcrypt, twilio_client, twilio_phone_number
from cliqcard_server.utils import format_phone_number, generate_access_token


class VerifyPhoneView(View):
    """
    View for receiving initial phone number request
    Should determine whether or not account exists
    """

    def dispatch_request(self):
        phone_number = request.json['phone_number']
        # validate/format phone number
        phone_number = format_phone_number(phone_number)
        if not phone_number:
            response = jsonify({
                'error': 'Invalid phone number. You must send phone numbers in valid international format.'
            })
            response.status_code = 400
            return response
        # create a random validation code
        code = ''.join(random.choice(string.digits) for _ in range(6))
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
        # # send the code to the phone number over SMS
        # twilio_client.messages.create(
        #     to=phone_number,
        #     from_=twilio_phone_number,
        #     body='Your CliqCard validation code is: %s' % code
        # )
        print('Code: %s' % code)
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


class GetRegistrationTokenView(View):
    """
    View that accepts a phone number and valid validation code and returns a token that lets new users
    complete account registration.
    """

    def dispatch_request(self):
        phone_number = request.json['phone_number']
        code = request.json['code']
        # validate/format phone number
        phone_number = format_phone_number(phone_number)
        if not phone_number:
            response = jsonify({
                'error': 'Invalid phone number. You must send phone numbers in valid international format.'
            })
            response.status_code = 400
            return response
        # try to find a matching phone token
        phone_token = PhoneToken.query.filter_by(phone_number=phone_number, code=code).first()
        if not phone_token:
            # invalid attempt
            abort(401)
        elif int(time.time()) > phone_token.expiration:
            # token is expired - delete from database
            db.session.delete(phone_token)
            db.session.commit()
            response = jsonify({
                'message': 'The validation code for that number has expired.'
            })
            response.status_code = 401
            return response
        else:
            # check to make sure there is not already an account with this number
            user = User.query.filter_by(phone_number=phone_number).first()
            if user is not None:
                # user already exists
                abort(401)
            # phone number validated, delete the phone token
            db.session.delete(phone_token)
            # delete any existing registration tokens for this phone number
            for registration_token in RegistrationToken.query.filter_by(phone_number=phone_number):
                db.session.delete(registration_token)
            # create a new registration token - use bcrypt to hash the raw token
            raw_token = secrets.token_urlsafe(64)
            registration_token = RegistrationToken(
                phone_number=phone_number,
                token=bcrypt.generate_password_hash(raw_token).decode('utf-8'),
                expiration=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            )
            db.session.add(registration_token)
            # commit the session
            db.session.commit()
            # respond with the registration token
            return jsonify({
                'phone_number': phone_number,
                'registration_token': raw_token,
                'expiration': registration_token.expiration
            })


class RefreshAccessTokenView(View):
    """
    Responds with a new access token given a valid refresh token.
    """

    def dispatch_request(self):
        token = request.json['refresh_token']
        # find the refresh token
        refresh_token = RefreshToken.query.filter_by(token=token).first()
        if not refresh_token:
            abort(401)
        # get the user
        user = refresh_token.user
        # generate a new access token
        access_token = generate_access_token(user.id)
        # respond with the new token
        return jsonify({
            'token': {
                'access_token': access_token,
                'refresh_token': refresh_token.token
            },
            'user': serialize_account(user)
        })