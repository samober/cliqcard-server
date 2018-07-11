from flask import request, abort, jsonify, Blueprint
from cliqcard_server.models import db, Email
from cliqcard_server.utils import require_oauth, current_token, format_phone_number
from cliqcard_server.serializers import serialize_email
from cliqcard_server.errors import InvalidRequestError, NotFoundError, UnauthorizedError


emails = Blueprint('emails', __name__, url_prefix='/emails')

@emails.route('/', methods=['GET', 'POST'])
@emails.route('/<int:email_id>', methods=['GET', 'PUT', 'DELETE'])
@require_oauth(None)
def index(email_id=None):
    if request.method == 'GET':
        # check for email id
        if email_id is not None:
            # return specific email
            email = Email.query.filter_by(id=email_id, user_id=current_token.user.id).first()
            if not email:
                raise NotFoundError()
            return jsonify(serialize_email(email))
        else:
            # return all emails
            emails = current_token.user.emails
            return jsonify(serialize_email(emails))
    elif request.method == 'POST':
        # add a new email
        type = request.json.get('type')
        address = request.json.get('address')
        # validate
        if not type:
            raise InvalidRequestError(message='Missing parameter \'type\'')
        if not address:
            raise InvalidRequestError(message='Missing parameter \'address\'')
        if type != 'personal' and type != 'work':
            raise InvalidRequestError(message='Invalid email type')
        # create the email
        email = Email()
        email.address = address
        email.type = type
        email.is_primary = False
        email.user_id = current_token.user.id
        # save
        db.session.add(email)
        db.session.commit()
        # return the email
        return jsonify(serialize_email(email))
    elif request.method == 'PUT':
        # find the email
        email = Email.query.filter_by(id=email_id, user_id=current_token.user.id).first()
        if not email:
            raise UnauthorizedError()
        # get the address
        address = request.json.get('address')
        # validate
        if not address:
            raise InvalidRequestError(message='Missing parameter \'address\'')
        # update the email
        email.address = address
        # save
        db.session.commit()
        # return the email
        return jsonify(serialize_email(email))
    elif request.method == 'DELETE':
        # find the email
        email = Email.query.filter_by(id=email_id, user_id=current_token.user.id).first()
        if not email:
            raise UnauthorizedError()
        # delete the email
        db.session.delete(email)
        db.session.commit()
        # return empty response
        return ('', 204)