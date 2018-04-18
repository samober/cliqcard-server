from flask import request, abort, jsonify
from flask.views import MethodView
from cliqcard_server.models import db, Address
from cliqcard_server.utils import require_token, format_phone_number
from cliqcard_server.serializers import serialize_card


class CardsView(MethodView):
    """
    Handles all the endpoints for manipulating cards.
    """

    @require_token
    def get(self, card_type):
        if not card_type:
            # return both cards
            personal_card = request.user.personal_card
            work_card = request.user.work_card
            return jsonify({
                'personal': serialize_card(personal_card),
                'work': serialize_card(work_card)
            })
        else:
            # return a specific card
            if card_type == 'personal':
                card = request.user.personal_card
            elif card_type == 'work':
                card = request.user.work_card
            else:
                card = None
            if not card:
                response = jsonify({
                    'error': "Only card types 'personal' and 'work' are allowed."
                })
                response.status_code = 400
                return response
            return jsonify(serialize_card(card))

    @require_token
    def put(self, card_type):
        if card_type == 'personal':
            card = request.user.personal_card
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
            card = request.user.work_card
            # format office phone
            office_phone = request.json.get('office_phone')
            if office_phone:
                office_phone = format_phone_number(office_phone)
            card.phone1 = office_phone
        else:
            abort(400)

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