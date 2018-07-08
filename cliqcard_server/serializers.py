import datetime
from cliqcard_server.models import Card
from authlib.flask.oauth2 import current_token

def iso8601(date):
    return date.isoformat()

def serialize_profile_picture(objects):
    def serialize(obj):
        return {
            'original': obj.original,
            'thumb_big': obj.thumb_big,
            'thumb_normal': obj.thumb_normal,
            'thumb_small': obj.thumb_small,
            'thumb_mini': obj.thumb_mini,
        }

    if not objects:
        return None
    elif isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    else:
        return serialize(objects)

def serialize_group_picture(objects):
    def serialize(obj):
        return {
            'original': obj.original,
            'thumb_big': obj.thumb_big,
            'thumb_normal': obj.thumb_normal,
            'thumb_small': obj.thumb_small,
            'thumb_mini': obj.thumb_mini,
        }

    if not objects:
        return None
    elif isinstance(objects, list):
        return [serialize(obj) for obj in objects]
    else:
        return serialize(objects)

def serialize_account(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'phone_number': obj.phone_number,
            'email': obj.email,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': '%s %s' % (obj.first_name, obj.last_name),
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'profile_picture': serialize_profile_picture(obj.profile_picture)
        }

    if not objects:
        return None
    elif isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    else:
        return serialize(objects)


def serialize_user(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': '%s %s' % (obj.first_name, obj.last_name),
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'profile_picture': serialize_profile_picture(obj.profile_picture)
        }

    if not objects:
        return None
    elif isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    else:
        return serialize(objects)


def serialize_address(objects):
    def serialize(obj):
        return {
            'street1': obj.street1,
            'street2': obj.street2,
            'city': obj.city,
            'state': obj.state,
            'zip': obj.zip,
            'country': obj.country
        }
    if not objects:
        return None
    elif isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    else:
        return serialize(objects)


def serialize_card(objects, omit_label=True):
    def serialize(obj):
        if obj.label == Card.CardLabel.personal:
            retval = {
                'id': obj.id,
                'created_at': iso8601(obj.created_at),
                'updated_at': iso8601(obj.updated_at),
                'label': 'personal',
                'cell_phone': obj.phone1,
                'home_phone': obj.phone2,
                'email': obj.email,
                'address': serialize_address(obj.address)
            }
            if omit_label:
                del retval['label']
            return retval
        else:
            retval = {
                'id': obj.id,
                'created_at': iso8601(obj.created_at),
                'updated_at': iso8601(obj.updated_at),
                'label': 'work',
                'office_phone': obj.phone1,
                'email': obj.email,
                'address': serialize_address(obj.address)
            }
            if omit_label:
                del retval['label']
            return retval
    if not objects:
        return None
    elif isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    else:
        return serialize(objects)


def serialize_group(objects):
    def serialize(obj):
        return {
            'id': obj.id,
            'created_at': iso8601(obj.created_at),
            'updated_at': iso8601(obj.updated_at),
            'name': obj.name,
            'member_count': obj.member_count,
            'picture': serialize_group_picture(obj.picture),
            'is_admin': obj.is_admin(current_token.user)
        }
    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)


def serialize_group_member(objects):
    def serialize(obj):
        return {
            'personal_card': obj.shares_personal_card,
            'work_card': obj.shares_work_card,
            'home_phone': obj.shares_home_phone,
            'cell_phone': obj.shares_cell_phone,
            'office_phone': obj.shares_office_phone
        }
    if isinstance(objects, list):
        return [ serialize(obj) for obj in objects ]
    elif not objects:
        return None
    else:
        return serialize(objects)