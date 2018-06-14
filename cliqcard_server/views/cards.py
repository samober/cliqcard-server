from flask import request, abort, jsonify, Blueprint
from cliqcard_server.models import db, Address
from cliqcard_server.utils import require_oauth, current_token, format_phone_number
from cliqcard_server.serializers import serialize_card
from cliqcard_server.errors import InvalidRequestError


cards = Blueprint('cards', __name__, url_prefix='/cards')


@cards.route('/', methods=['GET'])
@cards.route('/<string:card_type>', methods=['GET', 'PUT'])
@require_oauth(None)
def get(card_type=None):
    if request.method == 'GET':
        if not card_type:
            # return both cards
            personal_card = current_token.user.personal_card
            work_card = current_token.user.work_card
            return jsonify({
                'personal': serialize_card(personal_card),
                'work': serialize_card(work_card)
            })
        else:
            # return a specific card
            if card_type == 'personal':
                card = current_token.user.personal_card
            elif card_type == 'work':
                card = current_token.user.work_card
            else:
                card = None
            if not card:
                raise InvalidRequestError("Only card types 'personal' and 'work' are allowed.")
            return jsonify(serialize_card(card))
    elif request.method == 'PUT':
        if card_type == 'personal':
            card = current_token.user.personal_card
            # format cell phone
            cell_phone = request.json.get('cell_phone')
            if cell_phone:
                cell_phone = format_phone_number(cell_phone)
            card.phone1 = cell_phone
            # format home phone
            home_phone = request.json.get('home_phone')
            if home_phone:
                home_phone = format_phone_number(home_phone)
            card.phone2 = home_phone
        elif card_type == 'work':
            card = current_token.user.work_card
            # format office phone
            office_phone = request.json.get('office_phone')
            if office_phone:
                office_phone = format_phone_number(office_phone)
            card.phone1 = office_phone
        else:
            raise InvalidRequestError("Only card types 'personal' and 'work' are allowed.")

        card.email = request.json.get('email')

        # delete old address if any
        if card.address is not None:
            db.session.delete(card.address)
        # parse new address
        address_json = request.json.get('address')
        # check to see if it is null or blank
        if address_json and (address_json.get('street1') or address_json.get('street2') or address_json.get('city') \
                or address_json.get('state') or address_json.get('zip') or address_json.get('country')):
            # not blank
            # create new address
            address = Address(
                street1=address_json.get('street1'),
                street2=address_json.get('street2'),
                city=address_json.get('city'),
                state=address_json.get('state'),
                zip=address_json.get('zip'),
                country=address_json.get('country')
            )
            address.card = card
            db.session.add(address)

        # commit session
        db.session.commit()
        return jsonify(serialize_card(card))