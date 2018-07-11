from flask import jsonify, Blueprint
from cliqcard_server.utils import require_oauth
from cliqcard_server.serializers import serialize_user, serialize_phone, serialize_email
from authlib.flask.oauth2 import current_token
from cliqcard_server.errors import NotFoundError
from cliqcard_server.models import User


contacts = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts.route('/', methods=['GET'])
@contacts.route('/<int:user_id>', methods=['GET'])
@require_oauth(None)
def get(user_id=None):
    if not user_id:
        # get all groups for this user
        groups = list(current_token.user.groups)
        group_members = []
        # loop through groups and build a list of distinct group members that are not the current user
        for group in groups:
            for group_member in group.group_members:
                if group_member.user.id != current_token.user.id:
                    group_members.append(group_member)

        # loop through group members and build the contact list
        contact_list = {}
        for group_member in group_members:
            # get the contact or create a new one
            contact = contact_list.get(group_member.user.id, serialize_user(group_member.user))
            # initialize phone and email lists
            if not contact.get('phones'):
                contact['phones'] = []
            if not contact.get('emails'):
                contact['emails'] = []
            # loop through the phones
            for phone in group_member.phones:
                if phone not in contact['phones']:
                    contact['phones'].append(phone)
            # loop through the emails
            for email in group_member.emails:
                if email not in contact['emails']:
                    contact['emails'].append(email)
            # update the contact list entry
            contact_list[group_member.user.id] = contact

        # loop through all the contacts and serialize the phones and emails
        serialized_contacts = []
        for contact in contact_list.values():
            contact['phones'] = serialize_phone(contact['phones'])
            contact['emails'] = serialize_email(contact['emails'])
            serialized_contacts.append(contact)

        # return the list
        return jsonify(serialized_contacts)
    else:
        # get a single contact with the specific user id
        # get all groups for this user
        groups = list(current_token.user.groups)
        group_members = []
        # loop through groups and build a list of all the group members with this user id
        for group in groups:
            for group_member in group.group_members:
                if group_member.user.id == user_id:
                    group_members.append(group_member)

        # make sure this person is a contact
        if len(group_members) == 0:
            raise NotFoundError()

        # get the user
        user = User.query.get(user_id)

        # build the contact
        contact = serialize_user(user)
        contact['phones'] = []
        contact['emails'] = []

        # find all the phones and emails
        for group_member in group_members:
            for phone in group_member.phones:
                if phone not in contact['phones']:
                    contact['phones'].append(phone)
            for email in group_member.emails:
                if email not in contact['emails']:
                    contact['emails'].append(email)

        # serialize the phones and emails
        contact['phones'] = serialize_phone(contact['phones'])
        contact['emails'] = serialize_email(contact['emails'])

        # return the contact
        return jsonify(contact)