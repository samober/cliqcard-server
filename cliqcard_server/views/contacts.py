from flask import jsonify, Blueprint
from cliqcard_server.utils import require_oauth
from cliqcard_server.serializers import serialize_user, serialize_address
from authlib.flask.oauth2 import current_token


contacts = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts.route('/', methods=['GET'])
@require_oauth(None)
def get():
    # get all groups for this user
    groups = list(current_token.user.groups)
    group_members = []
    # loop through groups and build a list of distinct group members
    for group in groups:
        for group_member in group.group_members:
            group_members.append(group_member)
    # loop through and find all the users
    users = []
    for group_member in group_members:
        if group_member.user not in users and group_member.user != current_token.user:
            users.append(group_member.user)

    # loop through the user ids and pick out info from all the group members
    contact_list = {}
    for user in users:
        contact = serialize_user(user)
        for group_member in group_members:
            if group_member.user == user:
                # check to see if we should look at the personal card
                if group_member.shares_personal_card:
                    # check to see if we need to initialize the personal card in the contact
                    if 'personal_card' not in contact:
                        contact['personal_card'] = {
                            'cell_phone': None,
                            'home_phone': None,
                            'email': user.personal_card.email,
                            'address': serialize_address(user.personal_card.address)
                        }
                    # check to see if they share their cell phone in this group member
                    if group_member.shares_cell_phone:
                        contact['personal_card']['cell_phone'] = user.personal_card.phone1
                    # check to see if they share their home phone in this group member
                    if group_member.shares_home_phone:
                        contact['personal_card']['home_phone'] = user.personal_card.phone2

                # check to see if we should look at the work card
                if group_member.shares_work_card:
                    # check to see if we need to initialize the work card in the contact
                    if 'work_card' not in contact:
                        contact['work_card'] = {
                            'office_phone': None,
                            'email': user.work_card.email,
                            'address': serialize_address(user.work_card.address)
                        }
                    # check to see if they share their office phone in this group member
                    if group_member.shares_office_phone:
                        contact['work_card']['office_phone'] = user.work_card.phone1
        # add the new contact to the list
        contact_list[user.id] = contact

    return jsonify(list(contact_list.values()))