from flask import request, abort, jsonify, Blueprint
from cliqcard_server.models import db, Phone
from cliqcard_server.utils import require_oauth, current_token, format_phone_number
from cliqcard_server.serializers import serialize_phone
from cliqcard_server.errors import InvalidRequestError, NotFoundError, UnauthorizedError


phones = Blueprint('phones', __name__, url_prefix='/phones')

@phones.route('/', methods=['GET', 'POST'])
@phones.route('/<int:phone_id>', methods=['GET', 'PUT', 'DELETE'])
@require_oauth(None)
def index(phone_id=None):
    if request.method == 'GET':
        # check for phone id
        if phone_id is not None:
            # return specific phone
            phone = Phone.query.filter_by(id=phone_id, user_id=current_token.user.id).first()
            if not phone:
                raise NotFoundError()
            return jsonify(serialize_phone(phone))
        else:
            # return all phones
            phones = current_token.user.phones
            return jsonify(serialize_phone(phones))
    elif request.method == 'POST':
        # add a new phone number
        type = request.json.get('type')
        number = request.json.get('number')
        extension = request.json.get('extension')
        # validate
        if not type:
            raise InvalidRequestError(message='Missing parameter \'type\'')
        if not number:
            raise InvalidRequestError(message='Missing parameter \'number\'')
        if type != 'mobile' and type != 'home' and type != 'work':
            raise InvalidRequestError(message='Invalid phone number type')
        # validate/format phone number
        number = format_phone_number(number)
        if not number:
            raise InvalidRequestError(
                'Invalid phone number. You must send phone numbers in e164 format')
        # create the phone number
        phone = Phone()
        phone.number = number
        phone.type = type
        phone.extension = extension
        phone.is_primary = False
        phone.user_id = current_token.user.id
        # save
        db.session.add(phone)
        db.session.commit()
        # return the phone number
        return jsonify(serialize_phone(phone))
    elif request.method == 'PUT':
        # find the phone
        phone = Phone.query.filter_by(id=phone_id, user_id=current_token.user.id).first()
        if not phone:
            raise UnauthorizedError()
        # get the number and extension
        number = request.json.get('number')
        extension = request.json.get('extension')
        # validate
        if not number:
            raise InvalidRequestError(message='Missing parameter \'number\'')
        # validate/format phone number
        number = format_phone_number(number)
        if not number:
            raise InvalidRequestError(
                'Invalid phone number. You must send phone numbers in e164 format')
        # update the number
        phone.number = number
        phone.extension = extension
        # save
        db.session.commit()
        # return the phone number
        return jsonify(serialize_phone(phone))
    elif request.method == 'DELETE':
        # find the phone
        phone = Phone.query.filter_by(id=phone_id, user_id=current_token.user.id).first()
        if not phone or phone.is_primary:
            raise UnauthorizedError()
        # delete the number
        db.session.delete(phone)
        db.session.commit()
        # return empty response
        return ('', 204)